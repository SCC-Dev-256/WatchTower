import asyncio
from datetime import datetime
from typing import Dict, Any
from app.core.connection.health_checker import HealthChecker
from app.core.auditing_log.system import LoggingSystem
from prometheus_client import Gauge, Counter

class HealthCheckService:
    """Service for performing health checks on encoders."""

    def __init__(self):
        self.health_checker = HealthChecker()
        self.logger = LoggingSystem()
        self.encoder_health_gauge = Gauge('encoder_health', 'Health status of encoders', ['encoder_id', 'metric'])
        self.cpu_usage_gauge = Gauge('encoder_cpu_usage', 'CPU usage of encoders', ['encoder_id'])
        self.memory_usage_gauge = Gauge('encoder_memory_usage', 'Memory usage of encoders', ['encoder_id'])
        self.network_throughput_gauge = Gauge('encoder_network_throughput', 'Network throughput of encoders', ['encoder_id'])
        self.alert_counter = Counter('encoder_alerts', 'Number of alerts triggered', ['encoder_id', 'alert_type'])

    async def check_encoder_health(self, encoder_id: str) -> Dict[str, Any]:
        """Check the health of a specific encoder."""
        try:
            health_data = await self.health_checker.get_encoder_health(encoder_id)
            # Log temperature and other metrics
            self.logger.log_event('health_check', f"Encoder {encoder_id} metrics: {health_data['metrics']}", 'info')

            # Send alerts for flagged issues
            if 'issues' in health_data:
                for issue in health_data['issues']:
                    self.logger.log_event('alert', f"Encoder {encoder_id} issue: {issue}", 'warning')
                    self.alert_counter.labels(encoder_id=encoder_id, alert_type=issue).inc()
                    # Send notification through notification manager
                    notification = {
                        'error_type': 'health_check',
                        'severity': 'warning',
                        'encoder_id': encoder_id,
                        'timestamp': datetime.now().isoformat(),
                        'category': 'encoder_health',
                        'message': f'Health check detected issue: {issue}',
                        'impact': {
                            'service_impact': 'degraded',
                            'affected_users': 'unknown'
                        }
                    }
                    if self.app.notification_manager.should_send_notification('warning', encoder_id):
                        self.app.notification_manager.send_grouped_notification(notification)

            # Update Prometheus metrics
            self.encoder_health_gauge.labels(encoder_id=encoder_id).set(health_data['status'])
            self.cpu_usage_gauge.labels(encoder_id=encoder_id).set(health_data['metrics']['cpu_usage'])
            self.memory_usage_gauge.labels(encoder_id=encoder_id).set(health_data['metrics']['memory_usage'])
            self.network_throughput_gauge.labels(encoder_id=encoder_id).set(health_data['metrics'].get('network_throughput', 0))

            return health_data
        except Exception as e:
            self.logger.log_event('health_check', f"Failed to check health for encoder {encoder_id}", 'error', error=str(e))
            return {'status': 'error', 'message': str(e)}

    async def check_all_encoders(self) -> Dict[str, Any]:
        """Check the health of all encoders."""
        try:
            encoders_health = await self.health_checker.get_all_encoders_health()
            for encoder_id, health_data in encoders_health.items():
                self.encoder_health_gauge.labels(encoder_id=encoder_id).set(health_data['status'])
                self.cpu_usage_gauge.labels(encoder_id=encoder_id).set(health_data['metrics']['cpu_usage'])
                self.memory_usage_gauge.labels(encoder_id=encoder_id).set(health_data['metrics']['memory_usage'])
                self.network_throughput_gauge.labels(encoder_id=encoder_id).set(health_data['metrics'].get('network_throughput', 0))
            return {'status': 'success', 'encoders': encoders_health}
        except Exception as e:
            self.logger.log_event('health_check', "Failed to check health for all encoders", 'error', error=str(e))
            return {'status': 'error', 'message': str(e)} 