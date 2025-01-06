from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from app.core.metrics.base_metrics import BaseMetricsService
from app.core.metrics.collector import MetricsCollector
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.errors.exceptions import LoadBalancerError
from app.services.encoder_service import EncoderService
import logging

class LoadBalancer(BaseMetricsService):
    def __init__(self, metrics_collector: MetricsCollector):
        super().__init__('load_balancer')
        self.metrics_collector = metrics_collector
        self.failover_groups = {}
        self.logger = logging.getLogger(__name__)

    async def monitor_stream_health(self):
        """Monitor stream health using centralized metrics"""
        for encoder_id, group in self.failover_groups.items():
            if encoder_id in group['active_streams']:
                encoder = await self.encoder_service.get_encoder(encoder_id)
                health = await self.metrics_collector.get_stream_health(encoder)

                # Check temperature and other metrics
                if health['metrics']['temperature'] > 80:
                    self.logger.warning(f"High temperature on encoder {encoder_id}: {health['metrics']['temperature']}°C")
                if health['metrics']['network_link_error_count'] > 10:
                    self.logger.warning(f"High network link error count on encoder {encoder_id}: {health['metrics']['network_link_error_count']}")
                if health['metrics']['dropped_frames_behavior'] == 'Stop':
                    self.logger.warning(f"Dropped frames behavior set to stop on encoder {encoder_id}")

                if not health['healthy'] or 'issues' in health:
                    self.logger.warning(f"Unhealthy stream on encoder {encoder_id}: {health.get('issues', 'Unknown issues')}")
                    if await self._should_trigger_failover(health):
                        await self._initiate_failover(encoder_id)

    async def _should_trigger_failover(self, health: Dict) -> bool:
        """Determine if failover should be triggered based on health data"""
        # Critical issues that require immediate failover
        critical_issues = {'high_frame_drop', 'encoder_overload', 'buffer_underrun'}
        
        if any(issue in critical_issues for issue in health['issues']):
            return True
            
        # Check warning count and history
        warning_threshold = 3
        if len(health['warnings']) >= warning_threshold:
            return True
            
        return False

    async def _handoff_stream(self, from_id: str, to_id: str) -> bool:
        """Handle streaming handoff between encoders"""
        try:
            # Get streaming config
            group = self.failover_groups[from_id]
            config = group['streaming_config']
            
            # Ensure backup is configured correctly
            if not await self._sync_encoder_config(from_id, to_id):
                return False
                
            # Start streaming on backup
            backup_encoder = await self.encoder_service.get_encoder(to_id)
            if not await backup_encoder.start_stream():
                return False
                
            # Wait for backup stream to stabilize
            await asyncio.sleep(2)
            
            # Verify backup stream health
            backup_health = await self.metrics_collector.get_stream_health(backup_encoder)
            if not backup_health['healthy']:
                self.logger.error(f"Backup stream unhealthy: {backup_health['issues']}")
                return False
                
            # Stop streaming on failing encoder
            primary_encoder = await self.encoder_service.get_encoder(from_id)
            await primary_encoder.stop_stream()
            
            # Update group status
            group['active_streams'].remove(from_id)
            group['active_streams'].add(to_id)
            group['last_failover'] = datetime.utcnow()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Stream handoff failed: {str(e)}")
            return False

    async def _sync_encoder_config(self, primary_id: str, backup_id: str) -> bool:
        """Synchronize streaming configuration between encoders"""
        try:
            group = self.failover_groups[primary_id]
            config = group['streaming_config']
            
            backup_encoder = await self.encoder_service.get_encoder(backup_id)
            await backup_encoder.configure_stream(
                rtmp_key=config.rtmp_key,
                resolution=config.resolution,
                bitrate=config.bitrate,
                fps=config.fps,
                start_stream=False
            )
            
            group['last_sync'] = datetime.utcnow()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to sync encoder config: {str(e)}")
            return False