import asyncio
from typing import Dict, Any
from app.core.connection.health_checker import HealthChecker
from app.core.logging.system import LoggingSystem
from prometheus_client import Gauge

class HealthCheckService:
    """Service for performing health checks on encoders."""

    def __init__(self):
        self.health_checker = HealthChecker()
        self.logger = LoggingSystem()
        self.encoder_health_gauge = Gauge('encoder_health', 'Health status of encoders', ['encoder_id'])

    async def check_encoder_health(self, encoder_id: str) -> Dict[str, Any]:
        """Check the health of a specific encoder."""
        try:
            health_data = await self.health_checker.get_encoder_health(encoder_id)
            self.encoder_health_gauge.labels(encoder_id=encoder_id).set(health_data['status'])
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
            return {'status': 'success', 'encoders': encoders_health}
        except Exception as e:
            self.logger.log_event('health_check', "Failed to check health for all encoders", 'error', error=str(e))
            return {'status': 'error', 'message': str(e)} 