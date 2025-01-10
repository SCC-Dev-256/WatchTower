from enum import Enum
from typing import Dict, Union, Optional, Any
import csv
from pathlib import Path
from .aja_constants import AJAStreamParams
from app.core.aja.machine_logic.helo_params import HeloParameters

class AJAParameterType(Enum):
    STRING = "string"
    INTEGER = "integer"
    ENUM = "enum"
    DATA = "data"

class AJAParameter:
    def __init__(self, name: str, description: str, param_type: AJAParameterType, 
                 default_value: Union[str, int], enum_values: Optional[list] = None):
        self.name = name
        self.description = description
        self.param_type = param_type
        self.default_value = default_value
        self.enum_values = enum_values.split(", ") if enum_values else None

class AJAParameterManager:
    """Manages AJA device parameters and validation"""
    
    def __init__(self):
        self.parameters: Dict[str, AJAParameter] = {}
        self._load_parameters()
        self.param_ranges = {
            AJAStreamParams.VIDEO_BITRATE: (1_000_000, 20_000_000),  # 1-20 Mbps
            AJAStreamParams.FRAME_RATE: (23.98, 60),
            AJAStreamParams.KEYFRAME_INTERVAL: (1, 300)
        }

    def _load_parameters(self):
        """Load parameters from CSV configuration"""
        csv_path = Path(__file__).parent.parent / "Utils" / "Parameter_Configuration_Table.csv"
        
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                param = AJAParameter(
                    name=row['Param Name'],
                    description=row['Description'],
                    param_type=AJAParameterType(row['Param Type'].lower()),
                    default_value=row['Default Value'],
                    enum_values=row['Enum Values'] if row['Param Type'].lower() == 'enum' else None
                )
                self.parameters[param.name] = param

    def get_parameter(self, name: str) -> Optional[AJAParameter]:
        """Get parameter configuration by name"""
        return self.parameters.get(name)

    def validate_value(self, param: str, value: Any) -> bool:
        """Validate parameter value against defined ranges"""
        helo_params = HeloParameters().device_parameters  # Access current parameters
        if param in self.param_ranges:
            min_val, max_val = self.param_ranges[param]
            return min_val <= float(value) <= max_val
        return True

class AJAReplicatorCommands:
    START_RECORDING = 1
    STOP_RECORDING = 2  
    START_STREAMING = 3
    STOP_STREAMING = 4
    SHUTDOWN = 5

class AJAMediaState:
    RECORD_STREAM = 0
    DATA_LAN = 1