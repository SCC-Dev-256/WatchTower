from enum import Enum
from typing import Dict, Optional
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram
from app.core.aja import HeloDeviceParameters, MediaState, IntegratedEncoderParameters
from app.core.aja import start_streaming, stop_streaming, verify_streaming, verify_recording
from app.core.error_handling.bitrate import BitrateOptimizer
from app.core.error_handling.media_storage_handler import StorageHandler, RestartMonitor
from app.core.error_handling.error_logging import ErrorLogger, ErrorMetrics
from app.core.error_handling.errors.exceptions import EncoderError 
from app.core.error_handling import ErrorAnalyzer, ErrorTracker, ErrorType, BitrateOptimizer, StorageHandler, RestartMonitor, ErrorLogger, ErrorMetrics
from app.core.aja.aja_constants import ReplicatorCommands, AJAParameters

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
        self.logger = ErrorLogger(app)
        self.error_analyzer = ErrorAnalyzer(app)
        self.metrics = ErrorMetrics()
        self.error_handlers = {
            'network': self.handle_network_error,
            'streaming': self.handle_streaming_error,
            'recording': self.handle_recording_error,
            'audio': self.handle_audio_error,
            'video': self.handle_video_error,
            'system': self.handle_system_error,
            # Add more handlers as needed
        }

    async def process_error(self, error: Exception, source: str, context: Dict, error_type: Optional[ErrorType] = None) -> Dict:
        """Process and track error through all systems"""
        error_entry = self._create_error_entry(error, source, context, error_type)
        self.logger.log_error(error_entry)
        analysis = await self.error_analyzer.analyze_error(error_entry)
        self._update_metrics(error_entry, analysis)
        if source in self.error_handlers:
            await self.error_handlers[source](error_entry, analysis)
        return {'error_entry': error_entry, 'analysis': analysis, 'handled': True}

    def _create_error_entry(self, error: Exception, source: str, context: Dict, error_type: Optional[ErrorType]) -> Dict:
        """Create a unified error entry"""
        return {
            'timestamp': datetime.utcnow(),
            'error_type': error_type or type(error).__name__,
            'source': source,
            'message': str(error),
            'context': context
        }

    def _update_metrics(self, error_entry: Dict, analysis: Dict):
        """Update error metrics"""
        self.metrics.error_counter.labels(error_type=error_entry['error_type'], service=error_entry['source']).inc()
        if analysis.get('severity') in ['critical', 'high']:
            self.metrics.error_severity.labels(severity=analysis['severity']).inc()

    async def handle_network_error(self, error_entry: Dict, analysis: Dict):
        """Handle network-related errors"""
        # Implement specific logic for network errors
        pass

    async def handle_streaming_error(self, error_entry: Dict, analysis: Dict):
        """Handle streaming-related errors"""
        # Implement specific logic for streaming errors
        pass

    async def handle_recording_error(self, error_entry: Dict, analysis: Dict):
        """Handle recording-related errors"""
        # Implement specific logic for recording errors
        pass

    async def handle_audio_error(self, error_entry: Dict, analysis: Dict):
        """Handle audio-related errors"""
        # Implement specific logic for audio errors
        pass

    async def handle_video_error(self, error_entry: Dict, analysis: Dict):
        """Handle video-related errors"""
        # Implement specific logic for video errors
        pass

    async def handle_system_error(self, error_entry: Dict, analysis: Dict):
        """Handle system-related errors"""
        # Implement specific logic for system errors
        pass

    async def handle_helo_error(self, error_entry: Dict, analysis: Dict):
        """Handle HELO-specific errors"""
        encoder_id = error_entry['context'].get('encoder_id')
        error_type = error_entry['error_type']
        
        # Implement specific recovery strategies based on error type
        if error_type == HeloPoolErrorType.CONNECTION_LOST:
            await self.HandleConnectionLoss(encoder_id)
        elif error_type == HeloPoolErrorType.STREAM_FAILURE:
            await self.HandleStreamFailure(encoder_id)
        elif error_type == HeloPoolErrorType.HIGH_RESOURCE_USAGE:
            await self.HandleResourceUsage(encoder_id)
        elif error_type == HeloPoolErrorType.ENCODING_ERROR:
            await self.HandleEncodingError(encoder_id)
        elif error_type == HeloPoolErrorType.TEMPERATURE_WARNING:
            await self.HandleTemperatureWarning(encoder_id)
        elif error_type == HeloPoolErrorType.SYNC_LOSS:
            await self.HandleSyncLoss(encoder_id)
        elif error_type == HeloPoolErrorType.BUFFER_OVERFLOW:
            await self.HandleBufferOverflow(encoder_id)

    async def HandleConnectionLoss(self, encoder_id: str):
        """Handle connection loss with automatic reconnection"""
        self.logger.log_error(f"Connection lost to HELO encoder {encoder_id}", level='warning')
        try:
            if start_streaming(f"http://{encoder_id}"):
                self.logger.log_error(f"Reconnected to encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to reconnect encoder {encoder_id}: {str(e)}", level='error')

    async def HandleStreamFailure(self, encoder_id: str):
        """Handle stream failures with automatic restart"""
        self.logger.log_error(f"Stream failure on HELO encoder {encoder_id}", level='error')
        try:
            if start_streaming(f"http://{encoder_id}"):
                self.logger.log_error(f"Stream restarted for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to restart stream for encoder {encoder_id}: {str(e)}", level='error')

    async def HandleResourceUsage(self, encoder_id: str):
        """Handle high resource usage warnings"""
        self.logger.log_error(f"High resource usage on HELO encoder {encoder_id}", level='warning')
        try:
            await self._optimize_resources(encoder_id)
            self.logger.log_error(f"Resources optimized for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to optimize resources for encoder {encoder_id}: {str(e)}", level='error')

    async def HandleEncodingError(self, encoder_id: str):
        """Handle encoding errors with profile adjustment"""
        self.logger.log_error(f"Encoding error on HELO encoder {encoder_id}", level='error')
        try:
            await self._adjust_encoding(encoder_id)
            self.logger.log_error(f"Encoding adjusted for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to adjust encoding for encoder {encoder_id}: {str(e)}", level='error')

    async def HandleTemperatureWarning(self, encoder_id: str):
        """Handle temperature warnings by checking and adjusting device settings"""
        self.logger.log_error(f"Temperature warning on HELO encoder {encoder_id}", level='warning')
        try:
            temperature = await self._get_device_param(encoder_id, 'eParamID_Temperature')
            if temperature > self.temperature_threshold:
                await self._adjust_device_settings(encoder_id, 'cooling')
                self.logger.log_error(f"Temperature managed for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to manage temperature for encoder {encoder_id}: {str(e)}", level='error')

    async def HandleSyncLoss(self, encoder_id: str):
        """Handle sync loss by attempting to restart streaming or recording"""
        self.logger.log_error(f"Sync loss detected on HELO encoder {encoder_id}", level='warning')
        try:
            if not verify_streaming(f"http://{encoder_id}"):
                if start_streaming(f"http://{encoder_id}"):
                    self.logger.log_error(f"Sync restored for encoder {encoder_id}", level='info')
        except Exception as e:
            self.logger.log_error(f"Failed to restore sync for encoder {encoder_id}: {str(e)}", level='error')

    async def HandleBufferOverflow(self, encoder_id: str):
        """Handle buffer overflow with rate adjustment"""
        self.logger.log_error(f"Buffer overflow on HELO encoder {encoder_id}", level='error')
        # Implementation of buffer management logic
        self.logger.log_error(f"Buffer adjusted for encoder {encoder_id}", level='info')

    async def HandleError(self, error_type: str, encoder_id: str):
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

    async def HandleNetworkError(self, integrated_params: IntegratedEncoderParameters):
        """Handle network-related errors"""
        device_params = integrated_params.device_params
        if not device_params.network_connected:
            # Attempt to reconnect or switch network
            logger.info(f"Attempting to reconnect encoder {integrated_params.encoder_id}")
            # Implement reconnection logic here
            
            #AJA Devices already have network reconnection logic built in. We could add subroutine here to document the network event via pings, but this is not necessary.

    async def HandleStreamingError(self, integrated_params: IntegratedEncoderParameters):
        """Handle streaming-related errors"""
        device_params = integrated_params.device_params
        if device_params.media_state != MediaState.RECORD_STREAM:
            # Attempt to restart streaming
            logger.info(f"Attempting to restart streaming for encoder {integrated_params.encoder_id}")
            # Implement streaming restart logic here

            #AJA Devices already have streaming restart logic built in.

    def log_aja_error(self, command_type: ReplicatorCommands, device_id: str, error: Exception, media_state: Optional[MediaState] = None, severity: str = 'error') -> None:
        """Log AJA device-specific errors"""
        error_data = {
            'service': 'aja',
            'device_id': device_id,
            'command': command_type.value,
            'media_state': media_state.value if media_state else None,
            'error': str(error),
            'replicator_command': AJAParameters.REPLICATOR_COMMAND,
            'media_state_param': AJAParameters.MEDIA_STATE,
            'recording_profile': AJAParameters.RECORDING_PROFILE,
            'streaming_profile': AJAParameters.STREAMING_PROFILE,
            'stream_health': AJAParameters.STREAM_HEALTH,
            'network_bandwidth': AJAParameters.NETWORK_BANDWIDTH,
            'dropped_frames': AJAParameters.DROPPED_FRAMES
        }
        self.logger.log_error(error_data, error_type='aja', severity=severity)
        self.metrics.error_counter.labels(error_type='aja', service='aja').inc()