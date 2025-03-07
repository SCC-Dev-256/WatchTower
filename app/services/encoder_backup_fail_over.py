from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from app.core.error_handling import MetricsService, MetricsCollector
from app.core.error_handling.decorators import HandleErrors
from app.core.error_handling.errors.exceptions import LoadBalancerError
from app.services.encoder_service import EncoderService
import logging
from app.core.aja.aja_device import AJADevice
from app.core.aja.aja_constants import AJAParameters

class LoadBalancer(MetricsService):
    def __init__(self, metrics_collector: MetricsCollector, aja_device: AJADevice):
        super().__init__('load_balancer')
        self.metrics_collector = metrics_collector
        self.aja_device = aja_device
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
                if health['metrics'][AJAParameters.NETWORK_BANDWIDTH] > 10:
                    self.logger.warning(f"High network bandwidth usage on encoder {encoder_id}: {health['metrics'][AJAParameters.NETWORK_BANDWIDTH]}")
                if health['metrics'][AJAParameters.DROPPED_FRAMES] > 10:
                    self.logger.warning(f"High dropped frames on encoder {encoder_id}: {health['metrics'][AJAParameters.DROPPED_FRAMES]}")

                if not health['healthy'] or 'issues' in health:
                    self.logger.warning(f"Unhealthy stream on encoder {encoder_id}: {health.get('issues', 'Unknown issues')}")
                    if await self.should_trigger_failover(health):
                        await self._initiate_failover(encoder_id)

    async def should_trigger_failover(self, health: Dict) -> bool:
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

    async def handoff_stream(self, from_id: str, to_id: str) -> bool:
        """Handle streaming handoff between encoders"""
        try:
            # Get streaming config
            group = self.failover_groups[from_id]
            config = group['streaming_config']
            
            # Ensure backup is configured correctly
            if not await self.sync_encoder_config(from_id, to_id):
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

    async def sync_encoder_config(self, primary_id: str, backup_id: str) -> bool:
        """Synchronize streaming configuration between encoders"""
        try:
            group = self.failover_groups[primary_id]
            config = group['streaming_config']

            backup_encoder = await self.encoder_service.get_encoder(backup_id)
            await self.aja_device.set_param(AJAParameters.STREAMING_PROFILE, config)

            group['last_sync'] = datetime.utcnow()
            return True

        except Exception as e:
            self.logger.error(f"Failed to sync encoder config: {str(e)}")
            return False