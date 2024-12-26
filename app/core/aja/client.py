from typing import Dict, Optional, Union
import aiohttp
import asyncio
from datetime import datetime
from requests.auth import HTTPDigestAuth
from app.core.aja_parameters import AJAParameterManager
from app.core.aja_constants import AJAStreamParams, AJAHELOEndpoints
from app.core.error_handling.exceptions import (
    AJAClientError, 
    EncoderConnectionError,
    EncoderAuthenticationError
)

class AJAHELOClient:
    """Unified AJA HELO REST API Client"""
    
    def __init__(self, ip_address: str, username: str = 'admin', 
                 password: str = 'admin', port: int = 80, timeout: int = 30):
        self.base_url = f"http://{ip_address}:{port}/config"
        self.auth = HTTPDigestAuth(username, password)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
        self.param_manager = AJAParameterManager()
        self._connection_retries = 3

    async def _make_request(self, action: str, param_id: str, 
                          value: Optional[Union[str, int]] = None) -> Dict:
        """Make authenticated request to HELO API using proper parameter format"""
        url = f"{self.base_url}?action={action}&paramid={param_id}"
        if value is not None:
            url = f"{url}&value={value}"

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(timeout=self.timeout)

            async with self.session.get(url, auth=self.auth) as response:
                if response.status == 401:
                    raise EncoderAuthenticationError("Invalid credentials")
                elif response.status >= 400:
                    await self._handle_api_error(response)
                return await response.json()

        except aiohttp.ClientConnectorError:
            raise EncoderConnectionError(f"Failed to connect to encoder at {self.base_url}")
        except Exception as e:
            raise AJAClientError(f"Request failed: {str(e)}")

    # Implement core HELO commands using official parameter IDs
    async def start_streaming(self) -> Dict:
        """Start streaming using ReplicatorCommand parameter"""
        return await self._make_request(
            action="set",
            param_id="eParamID_ReplicatorCommand",
            value=3  # START_STREAMING from AJA example
        )

    async def stop_streaming(self) -> Dict:
        """Stop streaming using ReplicatorCommand parameter"""
        return await self._make_request(
            action="set",
            param_id="eParamID_ReplicatorCommand",
            value=4  # STOP_STREAMING from AJA example
        )

    # Add other methods following AJA's parameter-based approach... 