import csv
from pathlib import Path
from typing import Dict, Optional, Union

class Parameter:
    def __init__(self, name: str, description: str, param_type: str, default_value: Union[str, int], enum_values: Optional[list] = None):
        self.name = name
        self.description = description
        self.param_type = param_type
        self.default_value = default_value
        self.enum_values = enum_values.split(", ") if enum_values else None

class ParameterConfig:
    """Manages parameters from the configuration table"""
    
    def __init__(self):
        self.parameters: Dict[str, Parameter] = {}
        self._load_parameters()

    def _load_parameters(self):
        """Load parameters from CSV configuration"""
        csv_path = Path(__file__).parent.parent / "Utils" / "Parameter_Configuration_Table.csv"
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                param = Parameter(
                    name=row['Param Name'],
                    description=row['Description'],
                    param_type=row['Param Type'],
                    default_value=row['Default Value'],
                    enum_values=row['Enum Values'] if row['Param Type'].lower() == 'enum' else None
                )
                self.parameters[param.name] = param

    def get_parameter(self, name: str) -> Optional[Parameter]:
        """Get parameter configuration by name"""
        return self.parameters.get(name)

    def get_parameters_in_range(self, start: int, end: int) -> Dict[str, Parameter]:
        """Get parameters within a specific range of indices"""
        return {name: param for i, (name, param) in enumerate(self.parameters.items()) if start <= i < end} 

    def get_temperature_parameter(self) -> Optional[Parameter]:
        """Get the system temperature parameter configuration."""
        return self.get_parameter("System Temperature") 