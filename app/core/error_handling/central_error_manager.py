from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging
from prometheus_client import Counter, Gauge, Histogram
from app.monitoring.error_analysis import ErrorAnalyzer
from app.monitoring.error_tracking import ErrorTracker
from app.core.error_handling.handlers import MonitoringErrorHandler
from app.core.error_handling.errors.error_types import ErrorType
from app.core.connection.helo_pool_error_handler import HeloPoolErrorType
from app.core.helo.helo_commands import (
    start_streaming, stop_streaming, verify_streaming, verify_recording
)
from app.core.error_handling.decorators import unified_error_handler
from app.core.error_handling.Bitrate.optimize_bitrate import BitrateOptimizer
from app.core.error_handling.media_storage_handler import StorageHandler
from app.core.error_handling.restart_monitor import RestartMonitor
from app.core.error_handling.decorators import unified_error_handler
from app.core.error_handling.ErrorLogging import ErrorLogger, ErrorMetrics

class CentralErrorManager:
    """Central Error Management System"""
    
    def __init__(self, app):
        self.app = app
        self.error_analyzer = ErrorAnalyzer(app)
        self.error_tracker = ErrorTracker(app)
        self.monitoring_handler = MonitoringErrorHandler(app)
        self.logger = ErrorLogger(app)
        self.bitrate_optimizer = BitrateOptimizer()
        self.storage_handler = StorageHandler()
        self.restart_monitor = RestartMonitor()
        self.metrics = ErrorMetrics()

    async def process_error(self, 
                          error: Exception, 
                          source: str,
                          context: Dict,
                          error_type: Optional[ErrorType] = None) -> Dict:
        """Process and track error through all systems"""
        
        # Create unified error entry
        error_entry = {
            'timestamp': datetime.utcnow(),
            'error_type': error_type or self._determine_error_type(error),
            'source': source,
            'message': str(error),
            'context': context
        }

        # Track in central system
        self.error_tracker.track_error(error, context)
        
        # Analyze error patterns
        analysis = await self.error_analyzer.analyze_error(error_entry)
        
        # Update metrics
        self._update_metrics(error_entry, analysis)
        
        # Handle specific error types
        if source == 'helo':
            await self._handle_helo_error(error_entry, analysis)
        elif source == 'monitoring':
            await self.monitoring_handler.handle_metric_error(
                context.get('encoder_id'),
                context.get('metric_type'),
                error
            )

        return {
            'error_entry': error_entry,
            'analysis': analysis,
            'handled': True
        }

    async def _handle_helo_error(self, error_entry: Dict, analysis: Dict):
        """Handle HELO-specific errors"""
        encoder_id = error_entry['context'].get('encoder_id')
        error_type = error_entry['error_type']
        
        # Implement specific recovery strategies based on error type
        if error_type == HeloPoolErrorType.TEMPERATURE_WARNING:
            # Example: Adjust device settings
            await self._adjust_device_settings(encoder_id, 'cooling')
        elif error_type == HeloPoolErrorType.SYNC_LOSS:
            # Example: Attempt to resync using a command from helo_commands
            if not verify_streaming(f"http://{encoder_id}"):
                stop_streaming(f"http://{encoder_id}")
                if start_streaming(f"http://{encoder_id}"):
                    self.logger.info(f"Sync restored for encoder {encoder_id}")
        elif error_type == HeloPoolErrorType.BANDWIDTH_ISSUE:
            await self._optimize_bitrate(encoder_id)
        elif error_type == HeloPoolErrorType.CORRUPTED_STORAGE:
            await self._handle_corrupted_storage(encoder_id)
        elif error_type == HeloPoolErrorType.INFINITE_RESTART:
            await self._monitor_restart_loop(encoder_id)

    @unified_error_handler("Optimize Bitrate", include_analysis=True)
    async def _optimize_bitrate(self, encoder_id: str):
        """Optimize bitrate to handle bandwidth issues"""
        self.logger.info(f"Optimizing bitrate for encoder {encoder_id}")
        
        # Retrieve current bitrate from device parameters
        current_bitrate = await self._get_device_param(encoder_id, 'Video Bit Rate')
        
        # Use BitrateOptimizer
        optimized_bitrate, status = self.bitrate_optimizer.optimize_bitrate()
        
        self.logger.info(f"Bitrate optimization: {status}")

        if optimized_bitrate != current_bitrate:
            await self._set_device_param(encoder_id, 'Video Bit Rate', optimized_bitrate)
            self.logger.info(f"Bitrate adjusted to {optimized_bitrate} for encoder {encoder_id}")

    async def _handle_corrupted_storage(self, encoder_id: str):
        """Handle corrupted storage errors"""
        self.logger.info(f"Handling corrupted storage for encoder {encoder_id}")
        
        # Use StorageHandler
        storage_paths = self.storage_handler.get_storage_paths_from_config(encoder_id)
        
        for path in storage_paths:
            await self.storage_handler.dismount_storage(encoder_id, path)

    async def _monitor_restart_loop(self, encoder_id: str):
        """Monitor and handle infinite restart loops by checking log patterns"""
        self.logger.info(f"Monitoring restart loop for encoder {encoder_id}")
        
        # Use RestartMonitor
        await self.restart_monitor.monitor_restart_loop(encoder_id)

    async def _take_preventive_action(self, encoder_id: str):
        """Take preventive action to stop restart loop"""
        # Placeholder logic for preventive action
        # This could involve resetting certain parameters or alerting an administrator
        pass

    def _update_metrics(self, error_entry: Dict, analysis: Dict):
        """Update unified metrics"""
        self.metrics['total_errors'].labels(
            error_entry['error_type'],
            error_entry['source']
        ).inc()
        
        if analysis['severity'] in ['critical', 'high']:
            self.metrics['active_errors'].labels(analysis['severity']).inc() 

