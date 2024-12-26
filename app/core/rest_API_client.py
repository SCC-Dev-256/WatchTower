import requests
from typing import Dict, Any
import logging

class AJADevice:
    """
    Client for interacting with AJA HELO encoder REST API.
    
    Provides methods for querying device status, controlling streaming/recording,
    and managing device configuration.

    Args:
        base_url (str): Base URL of the encoder API
        timeout (int, optional): Request timeout in seconds. Defaults to 10.
        
    Examples:
        ```python
        device = AJADevice("http://192.168.1.100")
        
        # Get system status
        status = await device.get_system_status()
        
        # Start streaming
        await device.set_param("eParamID_ReplicatorStreamState", 1)
        ```
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(__name__)
        
    def get_param(self, paramid: str) -> Dict[str, Any]:
        """Get parameter value from AJA device"""
        url = f"{self.base_url}/config?action=get&paramid={paramid}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
        
    def set_param(self, paramid: str, value: Any) -> Dict[str, Any]:
        """Set parameter value on AJA device"""
        url = f"{self.base_url}/config?action=set&paramid={paramid}&value={value}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive device status"""
        try:
            stream_state = self.get_param("eParamID_ReplicatorStreamState")
            record_state = self.get_param("eParamID_ReplicatorRecordState")
            video_input = self.get_param("eParamID_VideoInSelect")
            
            return {
                "streaming": stream_state["value"] == 2,
                "recording": record_state["value"] == 2,
                "video_input": video_input["value"],
                "online": True
            }
        except Exception as e:
            self.logger.error(f"Error getting device status: {str(e)}")
            return {
                "streaming": False,
                "recording": False,
                "video_input": None,
                "online": False
            } 