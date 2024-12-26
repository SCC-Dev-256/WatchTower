from typing import Dict
from .handlers import ErrorHandler
from .exceptions import StreamError

class StreamErrorHandler(ErrorHandler):
    """Specialized handler for streaming-related errors"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.stream_thresholds = app.config.get('STREAM_THRESHOLDS', {})

    async def handle_stream_error(self, encoder_id: str, stream_data: Dict, error: Exception) -> Dict:
        """Handle streaming-related errors"""
        error_data = self._prepare_error_data(error, {
            'encoder_id': encoder_id,
            'stream_data': stream_data
        })

        # Analyze stream health
        health_check = await self._check_stream_health(encoder_id)
        if health_check['critical']:
            return await self._handle_critical_stream_failure(error_data)

        # Handle normal stream issues
        return await self._handle_stream_issue(error_data)

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