from typing import Dict, Optional
import aiohttp
from contextlib import asynccontextmanager
from app.core.error_handling import APIError, ErrorLogger
import asyncio
from prometheus_client import Gauge, Counter
import logging

class PoolManager:
    """Connection Pool Manager with Adaptive Sizing and Rate Limiting"""
    
    def __init__(self, 
                 error_logger: Optional[ErrorLogger] = None,
                 max_connections: int = 100,
                 min_connections: int = 10,
                 max_keepalive_time: int = 30,
                 rate_limit: int = 100):
        self.pools: Dict[str, aiohttp.ClientSession] = {}
        self.error_logger = error_logger
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_keepalive_time = max_keepalive_time
        self.rate_limit = rate_limit
        self._locks: Dict[str, asyncio.Lock] = {}
        self.connection_gauge = Gauge('active_connections', 'Number of active connections')
        self.request_counter = Counter('requests_total', 'Total number of requests', ['service', 'endpoint'])
        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def connection(self, service: str, endpoint: str):
        """Get a connection from the pool with error handling and rate limiting"""
        if service not in self._locks:
            self._locks[service] = asyncio.Lock()
            
        try:
            async with self._locks[service]:
                if service not in self.pools:
                    self.pools[service] = await self._create_session()
                    
                # Rate limiting logic
                self.request_counter.labels(service=service, endpoint=endpoint).inc()
                if self.request_counter.labels(service=service, endpoint=endpoint)._value.get() > self.rate_limit:
                    raise APIError(f"Rate limit exceeded for {service} at {endpoint}", code=429)

                try:
                    yield self.pools[service]
                except Exception as e:
                    self.error_logger.log_error({
                        'service': service,
                        'endpoint': endpoint,
                        'error': str(e)
                    }, 'api')
                    raise APIError(f"Connection error: {str(e)}", code=500)
        except Exception as e:
            self.error_logger.log_error({
                'service': service,
                'endpoint': endpoint,
                'error': str(e)
            }, 'critical')
            raise

    async def _create_session(self) -> aiohttp.ClientSession:
        """Create a new session with configured limits"""
        self._adjust_pool_size()
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit=self.max_connections,
                ttl_dns_cache=self.max_keepalive_time
            )
        )

    def _adjust_pool_size(self):
        """Adjust the pool size based on demand and system load"""
        # Example logic to adjust pool size
        current_load = self.connection_gauge._value.get()
        if current_load > self.max_connections * 0.8:
            self.max_connections = min(self.max_connections + 10, 200)
        elif current_load < self.min_connections * 0.5:
            self.max_connections = max(self.max_connections - 10, self.min_connections)
        self.connection_gauge.set(self.max_connections)

    async def cleanup(self):
        """Clean up all connection pools"""
        for service, session in self.pools.items():
            try:
                await session.close()
            except Exception as e:
                self.error_logger.log_error({
                    'service': service,
                    'action': 'cleanup',
                    'error': str(e)
                }, 'critical') 