import requests
from typing import Dict, Any

class AJADevice:
    """Custom AJA device interface"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_param(self, param_id: str) -> Dict[str, Any]:
        """Get parameter value from device"""
        response = self.session.get(f"{self.base_url}/api/parameters/{param_id}")
        response.raise_for_status()
        return response.json()
    
    def set_param(self, param_id: str, value: Any) -> Dict[str, Any]:
        """Set parameter value on device"""
        response = self.session.post(
            f"{self.base_url}/api/parameters/{param_id}",
            json={"value": value}
        )
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        response = self.session.get(f"{self.base_url}/api/status")
        response.raise_for_status()
        return response.json() 