from typing import Dict, Set, Optional, Callable, List
import asyncio
import logging
from datetime import datetime, timedelta
from prometheus_client import Counter, Gauge, Histogram
from app.core.connection.helo_pool_manager import HeloPoolManager
from app.core.error_handling.ErrorLogging import ErrorMetrics

class ConnectionWarmupMetrics:
    """Metrics for connection warmup monitoring"""
    warmup_attempts = Counter('helo_warmup_attempts_total', 'Connection warmup attempts', ['encoder_id'])
    warmup_success = Counter('helo_warmup_success_total', 'Successful warmups', ['encoder_id'])
    warmup_duration = Histogram('helo_warmup_duration_seconds', 'Warmup duration')
    warm_connections = Gauge('helo_warm_connections', 'Number of warm connections', ['encoder_id'])

class HeloWarmupManager:
    """Manages connection warmup for HELO devices"""
    
    def __init__(self, 
                 pool_manager: HeloPoolManager,
                 metrics: ErrorMetrics,
                 max_warm_connections: int = 3,
                 warmup_interval: int = 300,  # 5 minutes
                 preemptive_warmup_schedule: Optional[Dict[str, List[int]]] = None):
        """
        Initialize the HeloWarmupManager.

        Args:
            pool_manager (HeloPoolManager): The pool manager to manage HELO connections.
            metrics (EnhancedErrorMetrics): Metrics for monitoring warmup performance.
            max_warm_connections (int): Maximum number of warm connections to maintain.
            warmup_interval (int): Interval in seconds for warmup checks.
            preemptive_warmup_schedule (Optional[Dict[str, List[int]]]): Schedule for preemptive warmups.

        Example:
            warmup_manager = HeloWarmupManager(pool_manager, metrics)
        """
        self.pool_manager = pool_manager
        self.metrics = metrics
        self.warmup_metrics = ConnectionWarmupMetrics()
        self.logger = logging.getLogger(__name__)
        
        self.max_warm_connections = max_warm_connections
        self.warmup_interval = warmup_interval
        self.preemptive_warmup_schedule = preemptive_warmup_schedule or {}
        
        self._warm_connections: Dict[str, Set[str]] = {}
        self._warmup_tasks: Dict[str, asyncio.Task] = {}
        self._last_used: Dict[str, datetime] = {}

    async def start_warmup(self, encoder_id: str):
        """
        Start connection warmup for an encoder.

        Args:
            encoder_id (str): The ID of the encoder to warm up.

        Example:
            await warmup_manager.start_warmup('encoder_1')
        """
        if encoder_id not in self._warmup_tasks:
            self._warmup_tasks[encoder_id] = asyncio.create_task(
                self._warmup_loop(encoder_id)
            )
            self._warm_connections[encoder_id] = set()
            self.logger.info(f"Started warmup for encoder {encoder_id}")

    async def get_warm_connection(self, encoder_id: str) -> Optional[str]:
        """
        Get a warm connection for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.

        Returns:
            Optional[str]: The ID of a warm connection if available, otherwise None.

        Example:
            connection_id = await warmup_manager.get_warm_connection('encoder_1')
        """
        if encoder_id in self._warm_connections and self._warm_connections[encoder_id]:
            connection_id = self._warm_connections[encoder_id].pop()
            self._last_used[connection_id] = datetime.utcnow()
            self.warmup_metrics.warm_connections.labels(encoder_id).dec()
            return connection_id
        return None

    async def _warmup_loop(self, encoder_id: str):
        """
        Maintain warm connections for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.

        This method runs indefinitely to ensure the encoder has the required number of warm connections.
        """
        while True:
            try:
                await self._maintain_warm_pool(encoder_id)
                await asyncio.sleep(self.warmup_interval)
            except Exception as e:
                self.logger.error(f"Error in warmup loop for {encoder_id}: {str(e)}")
                await asyncio.sleep(self.warmup_interval * 2)  # Back off on error

    async def _maintain_warm_pool(self, encoder_id: str):
        """
        Maintain the pool of warm connections.

        Args:
            encoder_id (str): The ID of the encoder.

        Ensures the number of warm connections does not fall below the specified maximum.
        """
        current_count = len(self._warm_connections[encoder_id])
        needed = self.max_warm_connections - current_count
        
        if needed > 0:
            self.logger.debug(f"Warming up {needed} connections for {encoder_id}")
            for _ in range(needed):
                await self._warmup_connection(encoder_id)

    async def _warmup_connection(self, encoder_id: str):
        """
        Warm up a single connection.

        Args:
            encoder_id (str): The ID of the encoder.

        This method attempts to establish and prepare a connection for use.
        """
        self.warmup_metrics.warmup_attempts.labels(encoder_id).inc()
        start_time = datetime.utcnow()
        
        try:
            # Get connection from pool
            async with self.pool_manager.get_helo_connection(encoder_id) as connection:
                # Perform warmup sequence
                await self._execute_warmup_sequence(connection)
                
                # Add to warm pool
                connection_id = id(connection)
                self._warm_connections[encoder_id].add(connection_id)
                self._last_used[connection_id] = datetime.utcnow()
                
                # Update metrics
                duration = (datetime.utcnow() - start_time).total_seconds()
                self.warmup_metrics.warmup_duration.observe(duration)
                self.warmup_metrics.warmup_success.labels(encoder_id).inc()
                self.warmup_metrics.warm_connections.labels(encoder_id).inc()
                
                self.logger.debug(f"Successfully warmed up connection for {encoder_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to warm up connection for {encoder_id}: {str(e)}")
            raise

    async def _execute_warmup_sequence(self, connection, custom_sequence: Optional[Callable] = None) -> bool:
        """
        Execute connection warmup sequence.

        Args:
            connection: The connection object to warm up.
            custom_sequence (Optional[Callable]): A custom sequence of steps for warming up.

        Returns:
            bool: True if the warmup sequence was successful, False otherwise.

        Example:
            success = await warmup_manager._execute_warmup_sequence(connection, custom_sequence=my_custom_sequence)
        """
        try:
            if custom_sequence:
                await custom_sequence(connection)
            else:
                # Default warmup sequence
                await connection.ping()
                await connection.get_status()
                await connection.prepare_configs()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Warmup sequence failed: {str(e)}")
            return False

    async def cleanup_stale_connections(self):
        """
        Clean up stale warm connections.

        This method removes connections that have not been used within a specified threshold.
        """
        stale_threshold = datetime.utcnow() - timedelta(seconds=self.warmup_interval * 2)
        
        for encoder_id in list(self._warm_connections.keys()):
            stale_connections = {
                conn_id for conn_id in self._warm_connections[encoder_id]
                if self._last_used.get(conn_id, datetime.min) < stale_threshold
            }
            
            for conn_id in stale_connections:
                self._warm_connections[encoder_id].remove(conn_id)
                del self._last_used[conn_id]
                self.warmup_metrics.warm_connections.labels(encoder_id).dec()
                self.logger.info(f"Removed stale connection {conn_id} for encoder {encoder_id}")

    async def stop_warmup(self, encoder_id: str):
        """
        Stop connection warmup for an encoder.

        Args:
            encoder_id (str): The ID of the encoder.

        Example:
            await warmup_manager.stop_warmup('encoder_1')
        """
        if encoder_id in self._warmup_tasks:
            self._warmup_tasks[encoder_id].cancel()
            del self._warmup_tasks[encoder_id]
            del self._warm_connections[encoder_id]
            self.logger.info(f"Stopped warmup for encoder {encoder_id}") 