from typing import Dict, Any
from app.core.database.models.encoder import HeloEncoder
from app.core.error_handling.errors.exceptions import EncoderError
from app.core.config.parameter_config import ParameterConfig

class HealthChecker:
    """Utility class for checking the health of encoders."""

    async def get_encoder_health(self, encoder_id: str) -> Dict[str, Any]:
        """Get health status of a specific encoder."""
        try:
            encoder = await HeloEncoder.query.get(encoder_id)
            if not encoder:
                raise EncoderError(f"Encoder {encoder_id} not found", encoder_id=encoder_id)

            # Fetch temperature data
            parameter_config = ParameterConfig()
            temperature_param = parameter_config.get_temperature_parameter()
            temperature = encoder.get_parameter_value(temperature_param.name)  # Assuming a method to get parameter value

            # Simulate health check logic
            health_status = {
                'status': 'healthy' if encoder.status == 'online' else 'unhealthy',
                'metrics': {
                    'cpu_usage': 50,  # Placeholder value
                    'memory_usage': 60,  # Placeholder value
                    'temperature': temperature  # New temperature metric
                }
            }
            return health_status
        except Exception as e:
            raise EncoderError(f"Failed to get health for encoder {encoder_id}: {str(e)}", encoder_id=encoder_id)

    async def get_all_encoders_health(self) -> Dict[str, Any]:
        """Get health status of all encoders."""
        encoders = await HeloEncoder.query.all()
        encoders_health = {}
        for encoder in encoders:
            encoders_health[encoder.id] = await self.get_encoder_health(encoder.id)
        return encoders_health 