from app.core.error_handling import handle_errors
from app.core.error_handling.errors.exceptions import EncoderError
from typing import Dict, List
import logging
from app.core.error_handling.errors.error_types import ErrorType
from app.core.metrics.base_metrics import BaseMetricsService
from datetime import datetime
import requests

class HealthChecker(BaseMetricsService):
    def __init__(self, encoder_service, alert_service):
        super().__init__('health_checker')
        self.encoder_service = encoder_service
        self.alert_service = alert_service
        self.health_history: List[Dict] = []

    async def check_encoder_health(self, encoder_id: str) -> Dict:
        await self.log_and_increment(
            'check_attempt',
            "Checking encoder health",
            tags={'encoder_id': encoder_id}
        )
        
        try:
            metrics = await self.encoder_service.get_metrics(encoder_id)
            health_status = self._analyze_health_metrics(metrics)
            
            await self.gauge(
                'health_score',
                health_status['score'],
                tags={'encoder_id': encoder_id}
            )
            
            # Store historical data
            self._store_health_history(encoder_id, health_status)
            
            # Trigger alerts if necessary
            if health_status['score'] < 0.7:
                self._trigger_alert(encoder_id, health_status)
            
            if health_status['issues']:
                await self.log_and_increment(
                    'health_issues',
                    "Health issues detected",
                    level='warning',
                    tags={
                        'encoder_id': encoder_id,
                        'score': health_status['score'],
                        'issues': str(health_status['issues'])
                    }
                )
            
            return health_status
            
        except Exception as e:
            await self.log_and_increment(
                'health_check_error',
                "Health check failed",
                level='error',
                tags={'encoder_id': encoder_id, 'error': str(e)}
            )
            raise EncoderError(
                f"Health check failed: {str(e)}",
                encoder_id=encoder_id,
                error_type=ErrorType.RESOURCE_NOT_FOUND
            )

    def _analyze_health_metrics(self, metrics: Dict) -> Dict:
        """Analyze health metrics with weighted averages"""
        score = 1.0
        issues = []

        # Weighted checks
        weights = {
            'cpu_usage': 0.3,
            'memory_usage': 0.3,
            'response_time': 0.2,
            'thermal_status': 0.2
        }

        # Check CPU usage
        if metrics.get('cpu_usage', 0) > 80:
            score -= weights['cpu_usage']
            issues.append('high_cpu_usage')

        # Check memory usage
        if metrics.get('memory_usage', 0) > 90:
            score -= weights['memory_usage']
            issues.append('high_memory_usage')

        # Check response time
        if metrics.get('response_time', 0) > 200:
            score -= weights['response_time']
            issues.append('slow_response_time')

        # Check thermal status
        if metrics.get('thermal_status', 'normal') != 'normal':
            score -= weights['thermal_status']
            issues.append('thermal_issue')

        return {
            'score': max(score, 0),  # Ensure score is not negative
            'issues': issues
        }

    def _store_health_history(self, encoder_id: str, health_status: Dict) -> None:
        """Store health check results for historical analysis"""
        self.health_history.append({
            'encoder_id': encoder_id,
            'timestamp': datetime.utcnow().isoformat(),
            'score': health_status['score'],
            'issues': health_status['issues']
        })

    def _trigger_alert(self, encoder_id: str, health_status: Dict) -> None:
        """Send alerts if health score is below threshold"""
        alert_message = (
            f"Health score for encoder {encoder_id} dropped below threshold. "
            f"Score: {health_status['score']}, Issues: {health_status['issues']}"
        )
        self.alert_service.send_alert(alert_message)

class AlertService:
    """Service to send alerts to external platforms"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_alert(self, message: str) -> None:
        """Send alert message to configured webhook"""
        payload = {'text': message}
        try:
            requests.post(self.webhook_url, json=payload)
        except Exception as e:
            logging.error(f"Failed to send alert: {str(e)}") 