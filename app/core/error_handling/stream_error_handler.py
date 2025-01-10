from typing import Dict
from app.core.error_handling.handlers import ErrorHandler
from app.core.error_handling.errors.exceptions import AJAStreamError
from app.core.aja.client import AJAHELOClient
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.error_logging import ErrorLogger
from app.core.error_handling.central_error_manager import CentralErrorManager

class StreamErrorHandler(ErrorHandler):
    """Specialized handler for streaming-related errors"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.stream_thresholds = app.config.get('STREAM_THRESHOLDS', {})
        self.logger = ErrorLogger(app)
        self.aja_client = AJAHELOClient(app.config['AJA_IP'])

    @handle_errors(operation='stream_error', error_type='stream', severity='critical')
    async def handle_stream_error(self, encoder_id: str, stream_data: Dict, error: Exception) -> Dict:
        """Handle streaming-related errors using CentralErrorManager"""
        # Use CentralErrorManager for centralized error handling
        central_manager = CentralErrorManager(self.app)
        error_response = await central_manager.handle_stream_error(encoder_id, stream_data, error)

        # Log the error using ErrorLogger
        self.logger.log_error({
            'encoder_id': encoder_id,
            'error': str(error),
            'stream_data': stream_data
        }, error_type='stream', severity='critical')

        # AJA-specific logic remains here
        health_check = await self._check_stream_health(encoder_id)
        if health_check['critical']:
            return await self._handle_critical_stream_failure(error_response['error_entry'])

        return await self._handle_stream_issue(error_response['error_entry'])

    async def _check_stream_health(self, encoder_id: str) -> Dict:
        """Check stream health metrics"""
        metrics = await self.app.encoder_service.get_metrics(encoder_id)
        
        return {
            'critical': any(
                metrics[key] > self.stream_thresholds[key]
                for key in ['packet_loss', 'latency', 'jitter']
                if key in metrics and key in self.stream_thresholds
            ),
            'metrics': metrics
        } 