from enum import Enum
from typing import Dict, Optional
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram
from app.monitoring.error_analysis import ErrorAnalyzer
from app.monitoring.error_tracking import ErrorTracker
from app.core.error_handling.errors.error_types import ErrorType
from app.core.aja.machine_logic.helo_commands import (
    start_streaming, stop_streaming, verify_streaming, verify_recording
)
from app.core.error_handling.decorators import unified_error_handler
from app.core.error_handling.Bitrate.optimize_bitrate import BitrateOptimizer
from app.core.error_handling.media_storage_handler import StorageHandler, RestartMonitor
from app.core.error_handling.error_logging import ErrorLogger, ErrorMetrics
from app.core.aja.machine_logic.helo_params import HeloDeviceParameters, MediaState 
from app.core.aja.translate_mach_logi.integrated_params import IntegratedEncoderParameters
from app.core.error_handling.errors.exceptions import EncoderError 

logger = logging.getLogger(__name__)

class HeloPoolErrorType(Enum):
    """HELO-specific error types"""
    CONNECTION_LOST = "connection_lost"
    STREAM_FAILURE = "stream_failure"
    HIGH_RESOURCE_USAGE = "high_resource_usage"
    ENCODING_ERROR = "encoding_error"
    NETWORK_LATENCY = "network_latency"
    TEMPERATURE_WARNING = "temperature_warning"
    SYNC_LOSS = "sync_loss"
    BUFFER_OVERFLOW = "buffer_overflow"
    AUTH_FAILURE = "auth_failure"
    CONFIG_ERROR = "config_error"

class CentralErrorManager:
    """Central Error Management System"""
    
    def __init__(self, app):
        self.app = app
        self.error_analyzer = ErrorAnalyzer(app)
        self.error_tracker = ErrorTracker(app)
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
        if error_type == HeloPoolErrorType.CONNECTION_LOST:
            await self._handle_connection_loss(encoder_id)
        elif error_type == HeloPoolErrorType.STREAM_FAILURE:
            await self._handle_stream_failure(encoder_id)
        elif error_type == HeloPoolErrorType.HIGH_RESOURCE_USAGE:
            await self._handle_resource_usage(encoder_id)
        elif error_type == HeloPoolErrorType.ENCODING_ERROR:
            await self._handle_encoding_error(encoder_id)
        elif error_type == HeloPoolErrorType.TEMPERATURE_WARNING:
            await self._handle_temperature_warning(encoder_id)
        elif error_type == HeloPoolErrorType.SYNC_LOSS:
            await self._handle_sync_loss(encoder_id)
        elif error_type == HeloPoolErrorType.BUFFER_OVERFLOW:
            await self._handle_buffer_overflow(encoder_id)

    async def _handle_connection_loss(self, encoder_id: str):
        """Handle connection loss with automatic reconnection"""
        self.logger.log_error(f"Connection lost to HELO encoder {encoder_id}", level='warning')
        try:
            if start_streaming(f"http://{encoder_id}"):
                self.logger.log_error(f"Reconnected to encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to reconnect encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_stream_failure(self, encoder_id: str):
        """Handle stream failures with automatic restart"""
        self.logger.log_error(f"Stream failure on HELO encoder {encoder_id}", level='error')
        try:
            if start_streaming(f"http://{encoder_id}"):
                self.logger.log_error(f"Stream restarted for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to restart stream for encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_resource_usage(self, encoder_id: str):
        """Handle high resource usage warnings"""
        self.logger.log_error(f"High resource usage on HELO encoder {encoder_id}", level='warning')
        try:
            await self._optimize_resources(encoder_id)
            self.logger.log_error(f"Resources optimized for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to optimize resources for encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_encoding_error(self, encoder_id: str):
        """Handle encoding errors with profile adjustment"""
        self.logger.log_error(f"Encoding error on HELO encoder {encoder_id}", level='error')
        try:
            await self._adjust_encoding(encoder_id)
            self.logger.log_error(f"Encoding adjusted for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to adjust encoding for encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_temperature_warning(self, encoder_id: str):
        """Handle temperature warnings by checking and adjusting device settings"""
        self.logger.log_error(f"Temperature warning on HELO encoder {encoder_id}", level='warning')
        try:
            temperature = await self._get_device_param(encoder_id, 'eParamID_Temperature')
            if temperature > self.temperature_threshold:
                await self._adjust_device_settings(encoder_id, 'cooling')
                self.logger.log_error(f"Temperature managed for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to manage temperature for encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_sync_loss(self, encoder_id: str):
        """Handle sync loss by attempting to restart streaming or recording"""
        self.logger.log_error(f"Sync loss detected on HELO encoder {encoder_id}", level='warning')
        try:
            if not verify_streaming(f"http://{encoder_id}"):
                if start_streaming(f"http://{encoder_id}"):
                    self.logger.log_error(f"Sync restored for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to restore sync for encoder {encoder_id}: {str(e)}", level='error')

    async def _handle_buffer_overflow(self, encoder_id: str):
        """Handle buffer overflow with rate adjustment"""
        self.logger.log_error(f"Buffer overflow on HELO encoder {encoder_id}", level='error')
        # Implementation of buffer management logic
        self.logger.log_error(f"Buffer adjusted for encoder {encoder_id}", level='info')

    def _update_metrics(self, error_entry: Dict, analysis: Dict):
        """Update unified metrics"""
        self.metrics['total_errors'].labels(
            error_entry['error_type'],
            error_entry['source']
        ).inc()
        
        if analysis['severity'] in ['critical', 'high']:
            self.metrics['active_errors'].labels(analysis['severity']).inc() 

    async def handle_stream_error(self, encoder_id: str, stream_data: Dict, error: Exception) -> Dict:
        """Centralized handling of streaming-related errors"""
        error_entry = {
            'timestamp': datetime.utcnow(),
            'error_type': 'stream_error',
            'source': 'stream_handler',
            'message': str(error),
            'context': {'encoder_id': encoder_id, 'stream_data': stream_data}
        }

        # Log the error
        self.logger.log_error(error_entry, level='critical')

        # Analyze error patterns
        analysis = await self.error_analyzer.analyze_error(error_entry)

        # Update metrics
        self._update_metrics(error_entry, analysis)

        return {
            'error_entry': error_entry,
            'analysis': analysis,
            'handled': True
        }

    async def handle_error(self, error_type: str, encoder_id: str):
        """Handle errors based on type and encoder parameters"""
        try:
            # Initialize parameters
            integrated_params = IntegratedEncoderParameters(encoder_id)
            device_params = integrated_params.device_params

            # Log current parameters
            logger.info(f"Handling {error_type} for encoder {encoder_id} with parameters: {device_params}")

            # Call the appropriate handler
            if error_type in self.error_handlers:
                await self.error_handlers[error_type](integrated_params)
            else:
                logger.error(f"No handler for error type: {error_type}")

        except Exception as e:
            logger.error(f"Failed to handle error {error_type} for encoder {encoder_id}: {str(e)}")
            raise EncoderError(f"Error handling failed for {encoder_id}", encoder_id=encoder_id)

    async def handle_network_error(self, integrated_params: IntegratedEncoderParameters):
        """Handle network-related errors"""
        device_params = integrated_params.device_params
        if not device_params.network_connected:
            # Attempt to reconnect or switch network
            logger.info(f"Attempting to reconnect encoder {integrated_params.encoder_id}")
            # Implement reconnection logic here

    async def handle_streaming_error(self, integrated_params: IntegratedEncoderParameters):
        """Handle streaming-related errors"""
        device_params = integrated_params.device_params
        if device_params.media_state != MediaState.RECORD_STREAM:
            # Attempt to restart streaming
            logger.info(f"Attempting to restart streaming for encoder {integrated_params.encoder_id}")
            # Implement streaming restart logic here

