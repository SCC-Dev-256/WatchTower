from typing import Optional, Dict, Any
from .pool_manager import PoolManager
from app.core.cablecast_IN_DEVELOPMENT.cablecast_constants import CablecastEndpoints
from app.core.error_handling import APIError, handle_errors
from app.core.error_handling.ErrorLogging import ErrorLogger
import json

class CablecastPooledClient:
    """Cablecast API Client with Connection Pooling"""
    
    def __init__(self, 
                 base_url: str,
                 api_key: Optional[str] = None,
                 service_name: str = "cablecast",
                 pool_manager: Optional[PoolManager] = None,
                 error_logger: Optional[ErrorLogger] = None):
        self.base_url = base_url
        self.service_name = service_name
        self.pool_manager = pool_manager or PoolManager()
        self.error_logger = error_logger
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    @handle_errors(include_analysis=True)
    async def request(self, 
                     endpoint: CablecastEndpoints,
                     method: str = "GET",
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request using the connection pool with error handling"""
        url = f"{self.base_url}{endpoint.value}"
        
        try:
            async with self.pool_manager.connection(self.service_name, endpoint.value) as session:
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            if self.error_logger:
                self.error_logger.log_error({
                    'service': self.service_name,
                    'endpoint': endpoint.value,
                    'error': str(e)
                }, 'api')
            raise APIError(f"Request failed: {str(e)}", code=500) 