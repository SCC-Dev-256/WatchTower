from app.core.config.parameter_config import ParameterConfig

class HeloParameters:
    """Encapsulates HELO device parameters for analysis"""

    def __init__(self):
        self.parameter_config = ParameterConfig()
        self._load_parameters()

    def _load_parameters(self):
        """Load specific parameters for HELO device"""
        params = self.parameter_config.get_parameters_in_range(842, 916)
        for name, param in params.items():
            setattr(self, self._format_param_name(name), param.default_value)

    def _format_param_name(self, name: str) -> str:
        """Format parameter name to a valid attribute name"""
        return name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")

# Example usage
helo_params = HeloParameters()
print(helo_params.ip_address)  # Access a specific parameter
