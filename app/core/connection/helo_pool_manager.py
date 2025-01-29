from contextlib import asynccontextmanager
from typing import Dict, Optional
import aiohttp
from datetime import datetime, timedelta
import asyncio
from prometheus_client import Counter, Gauge, Histogram
from app.services.encoder_manager import EncoderManager
from app.core.connection import PoolManager 
from app.core.error_handling import HeloErrorType, HeloErrorHandler

class HeloConnectionMetrics:
    """HELO-specific connection metrics"""
    active_helo_connections = Gauge('helo_active_connections', 'Number of active HELO connections')
    helo_connection_errors = Counter('helo_connection_errors', 'HELO connection errors', ['error_type'])
    helo_connection_latency = Histogram('helo_connection_latency', 'HELO connection latency')
    helo_stream_health = Gauge('helo_stream_health', 'HELO stream health metrics', ['metric_type'])

class HeloPoolManager:
    """Specialized Connection Pool Manager for AJA HELO devices"""
    
    def __init__(self, 
                 encoder_manager: EncoderManager,
                 pool_manager: PoolManager,
                 error_handler: HeloErrorHandler,
                 max_idle_time: int = 300,  # 5 minutes
                 max_lifetime: int = 3600):  # 1 hour
        self.encoder_manager = encoder_manager
        self.pool_manager = pool_manager
        self.error_handler = error_handler
        self.max_idle_time = max_idle_time
        self.max_lifetime = max_lifetime
        self.metrics = HeloConnectionMetrics()
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
        self._connection_timestamps: Dict[str, datetime] = {}

    async def start_health_monitoring(self, encoder_id: str):
        """Start health monitoring for a HELO device"""
        if encoder_id not in self._health_check_tasks:
            self._health_check_tasks[encoder_id] = asyncio.create_task(
                self._monitor_helo_health(encoder_id)
            )

    async def _monitor_helo_health(self, encoder_id: str):
        """Monitor HELO device health with enhanced error handling"""
        while True:
            try:
                client = await self.encoder_manager.get_client(encoder_id)
                health_data = await client.get_health_metrics()
                
                # Check for warning conditions and handle errors
                if health_data['cpu_usage'] > 80:
                    await self.error_handler.handle_error(
                        HeloErrorType.HIGH_RESOURCE_USAGE,
                        encoder_id,
                        {'cpu_usage': health_data['cpu_usage']}
                    )
                
                if health_data['temperature'] > 75:
                    await self.error_handler.handle_error(
                        HeloErrorType.TEMPERATURE_WARNING,
                        encoder_id,
                        {'temperature': health_data['temperature']}
                    )
                    
                # Check for encoding issues
                if health_data.get('encoding_errors', 0) > 0:
                    await self.error_handler.handle_error(
                        HeloErrorType.ENCODING_ERROR,
                        encoder_id,
                        {'errors': health_data['encoding_errors']}
                    )
                    
            except Exception as e:
                await self.error_handler.handle_error(
                    HeloErrorType.CONNECTION_LOST,
                    encoder_id,
                    {'error': str(e)}
                )
            
            await asyncio.sleep(self.health_check_interval)

    @asynccontextmanager
    async def get_helo_connection(self, encoder_id: str):
        """Get a connection to a HELO device with automatic retry and failover"""
        self.metrics.active_helo_connections.inc()
        
        try:
            async with self.pool_manager.connection("helo", f"encoder_{encoder_id}") as session:
                start_time = datetime.now()
                self._connection_timestamps[encoder_id] = start_time
                try:
                    yield session
                finally:
                    duration = (datetime.now() - start_time).total_seconds()
                    self.metrics.helo_connection_latency.observe(duration)
        except Exception as e:
            self.metrics.helo_connection_errors.labels(type(e).__name__).inc()
            raise
        finally:
            self.metrics.active_helo_connections.dec()

    async def cleanup(self):
        """Cleanup all HELO connections and monitoring tasks"""
        current_time = datetime.now()
        for encoder_id, start_time in list(self._connection_timestamps.items()):
            if (current_time - start_time).total_seconds() > self.max_lifetime:
                # Forcefully close connections exceeding max lifetime
                await self.pool_manager.pools[f"encoder_{encoder_id}"].close()
                del self._connection_timestamps[encoder_id]
        
        for task in self._health_check_tasks.values():
            task.cancel()
        await asyncio.gather(*self._health_check_tasks.values(), return_exceptions=True)
        self._health_check_tasks.clear() 