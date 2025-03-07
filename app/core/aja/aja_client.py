from typing import Dict, Optional, Union
import aiohttp
import asyncio
from datetime import datetime
from app.core.aja.aja_helo_parameter_service import AJAParameterManager
from app.core.aja.aja_constants import AJAStreamParams
from app.core.error_handling import AJAClientError
from enum import Enum

class AJAHELOEndpoints(Enum):
    # Control endpoints
    STREAM_START = "/control/stream/start"
    STREAM_STOP = "/control/stream/stop"
    RECORD_START = "/control/record/start"
    RECORD_STOP = "/control/record/stop"
    REBOOT = "/control/reboot"
    
    # Status endpoints
    SYSTEM_STATUS = "/status/system"
    STREAM_STATUS = "/status/streaming"
    RECORD_STATUS = "/status/recording"
    NETWORK_STATUS = "/status/network"
    MEDIA_STATUS = "/status/media"
    
    # Configuration endpoints
    STREAM_CONFIG = "/config/stream"
    RECORD_CONFIG = "/config/record"
    NETWORK_CONFIG = "/config/network"
    SYSTEM_CONFIG = "/config/system"

class AJAHELOClient:
    """Enhanced AJA HELO REST API Client"""
    
    def __init__(self, ip_address: str, port: int = 80, timeout: int = 30):
        self.base_url = f"http://{ip_address}:{port}/api/v1"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
        self._last_error = None
        self._connection_retries = 3

    async def _handle_api_error(self, response: aiohttp.ClientResponse) -> None:
        """Handle API error responses"""
        error_data = await response.json()
        error_msg = error_data.get('error', 'Unknown error')
        
        if response.status == 400:
            raise AJAClientError(f"Invalid request: {error_msg}")
        elif response.status == 401:
            raise AJAClientError("Authentication required")
        elif response.status == 403:
            raise AJAClientError("Operation not permitted")
        elif response.status == 404:
            raise AJAClientError(f"Resource not found: {error_msg}")
        elif response.status == 409:
            raise AJAClientError(f"Operation conflict: {error_msg}")
        else:
            raise AJAClientError(f"API error ({response.status}): {error_msg}")

    async def make_request(self, method: str, endpoint: Union[str, AJAHELOEndpoints], 
                          **kwargs) -> Dict:
        """Make authenticated request with retries and error handling"""
        if isinstance(endpoint, AJAHELOEndpoints):
            endpoint = endpoint.value

        url = f"{self.base_url}{endpoint}"
        retries = self._connection_retries

        while retries > 0:
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession(timeout=self.timeout)

                async with self.session.request(method, url, **kwargs) as response:
                    if response.status >= 400:
                        await self._handle_api_error(response)
                    return await response.json()

            except aiohttp.ClientConnectorError:
                retries -= 1
                if retries == 0:
                    raise AJAClientError("Failed to connect to encoder")
                await asyncio.sleep(1)

            except aiohttp.ClientError as e:
                self._last_error = str(e)
                raise AJAClientError(f"Connection error: {str(e)}")

    # Enhanced streaming control methods
    async def start_stream(self, config: Optional[Dict] = None) -> Dict:
        """Start streaming with optional configuration"""
        if config:
            await self.configure_stream(config)
        return await self.make_request("POST", AJAHELOEndpoints.STREAM_START)

    async def stop_stream(self) -> Dict:
        """Stop current stream"""
        return await self.make_request("POST", AJAHELOEndpoints.STREAM_STOP)

    # Enhanced recording control methods
    async def start_recording(self, config: Optional[Dict] = None) -> Dict:
        """Start recording with optional configuration"""
        if config:
            await self.configure_recording(config)
        return await self.make_request("POST", AJAHELOEndpoints.RECORD_START)

    async def stop_recording(self) -> Dict:
        """Stop current recording"""
        return await self.make_request("POST", AJAHELOEndpoints.RECORD_STOP)

    # System control methods
    async def reboot_device(self) -> Dict:
        """Reboot the HELO device"""
        return await self.make_request("POST", AJAHELOEndpoints.REBOOT)

    # Enhanced status methods with error handling
    async def get_full_status(self) -> Dict:
        """Get comprehensive device status"""
        try:
            status_results = await asyncio.gather(
                self.make_request("GET", AJAHELOEndpoints.SYSTEM_STATUS),
                self.make_request("GET", AJAHELOEndpoints.STREAM_STATUS),
                self.make_request("GET", AJAHELOEndpoints.RECORD_STATUS),
                self.make_request("GET", AJAHELOEndpoints.NETWORK_STATUS),
                return_exceptions=True
            )

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'system': status_results[0] if not isinstance(status_results[0], Exception) else None,
                'streaming': status_results[1] if not isinstance(status_results[1], Exception) else None,
                'recording': status_results[2] if not isinstance(status_results[2], Exception) else None,
                'network': status_results[3] if not isinstance(status_results[3], Exception) else None,
                'errors': [str(r) for r in status_results if isinstance(r, Exception)]
            }
        except Exception as e:
            raise AJAClientError(f"Failed to get device status: {str(e)}")

    async def configure_stream(self, config: Dict) -> Dict:
        """Configure streaming parameters"""
        # Validate all parameters before sending
        for param, value in config.items():
            if not self.param_manager.validate_value(param, value):
                raise AJAClientError(f"Invalid value for parameter: {param}")

        return await self.make_request("POST", AJAHELOEndpoints.STREAM_CONFIG, json=config)

    async def get_network_stats(self) -> Dict:
        """Get network statistics"""
        return await self.make_request("GET", AJAHELOEndpoints.NETWORK_STATUS)

    async def get_media_status(self) -> Dict:
        """Get media and storage status"""
        return await self.make_request("GET", AJAHELOEndpoints.MEDIA_STATUS)

    async def configure_recording(self, config: Dict) -> Dict:
        """Configure recording parameters"""
        # Validate all parameters before sending
        for param, value in config.items():
            if not self.param_manager.validate_value(param, value):
                raise AJAClientError(f"Invalid value for parameter: {param}")

        return await self.make_request("POST", AJAHELOEndpoints.RECORD_CONFIG, json=config)

    async def configure_network(self, config: Dict) -> Dict:
        """Configure network parameters"""
        # Validate all parameters before sending
        for param, value in config.items():
            if not self.param_manager.validate_value(param, value):
                raise AJAClientError(f"Invalid value for parameter: {param}")

        return await self.make_request("POST", AJAHELOEndpoints.NETWORK_CONFIG, json=config)

    async def configure_system(self, config: Dict) -> Dict:
        """Configure system parameters"""
        # Validate all parameters before sending
        for param, value in config.items():
            if not self.param_manager.validate_value(param, value):
                raise AJAClientError(f"Invalid value for parameter: {param}")

        return await self.make_request("POST", AJAHELOEndpoints.SYSTEM_CONFIG, json=config)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
  