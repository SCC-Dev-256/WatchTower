from typing import Dict
from app.core.error_handling.handlers import ErrorHandler
from app.core.error_handling.decorators import handle_errors

class MonitoringErrorHandler(ErrorHandler):
    """Specialized handler for monitoring-related errors"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.alert_thresholds = app.config.get('ALERT_THRESHOLDS', {})

    async def handle_metric_error(self, encoder_id: str, metric_type: str, error: Exception) -> Dict:
        """Handle metric collection errors"""
        error_data = self._prepare_error_data(error, {
            'encoder_id': encoder_id,
            'metric_type': metric_type
        })

        # Check if this is a critical metric
        if metric_type in self.alert_thresholds.get('critical_metrics', []):
            return await self._handle_critical_metric_failure(error_data)

        # Handle non-critical metric failure
        return await self._handle_normal_metric_failure(error_data)

    async def handle_alert_error(self, alert_data: Dict, error: Exception) -> Dict:
        """Handle alert processing errors"""
        error_data = self._prepare_error_data(error, alert_data)
        
        if alert_data.get('severity') == 'critical':
            return await self._handle_critical_alert_failure(error_data)
            
        return await self._handle_normal_alert_failure(error_data) 