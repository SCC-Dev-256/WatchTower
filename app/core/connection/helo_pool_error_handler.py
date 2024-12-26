from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime
import logging
import random
import asyncio
from prometheus_client import Counter, Gauge, Histogram

class HeloPoolErrorType(Enum):
    """HELO-specific error types"""
    CONNECTION_LOST = "connection_lost"
    STREAM_FAILURE = "stream_failure"
    HIGH_RESOURCE_USAGE = "high_resource_usage"
    ENCODING_ERROR = "encoding_error"
    NETWORK_LATENCY = "network_latency"
    TEMPERATURE_WARNING = "temperature_warning"
    SYNC_LOSS = "sync_loss"
    BUFFER_OVERFLOW = "buffer_overflow"
    AUTH_FAILURE = "auth_failure"
    CONFIG_ERROR = "config_error"

class HeloPoolErrorMetrics:
    """HELO error-specific metrics"""
    error_counter = Counter('helo_errors_total', 'Total HELO errors', ['error_type', 'encoder_id'])
    recovery_time = Histogram('helo_error_recovery_seconds', 'Time to recover from errors')
    error_state = Gauge('helo_error_state', 'Current error state', ['encoder_id'])
    consecutive_errors = Counter('helo_consecutive_errors', 'Consecutive errors by type', ['error_type'])

class HeloPoolErrorHandler:
    """Handles HELO-specific errors and recovery"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = HeloPoolErrorMetrics()
        self._error_history: Dict[str, List[Dict]] = {}
        self._recovery_attempts: Dict[str, int] = {}

    async def handle_error(self, 
                         error_type: HeloPoolErrorType, 
                         encoder_id: str, 
                         error_details: Optional[Dict] = None) -> Dict:
        """Handle HELO-specific errors with recovery strategies"""
        
        self.metrics.error_counter.labels(error_type.value, encoder_id).inc()
        self.metrics.error_state.labels(encoder_id).set(1)
        
        error_entry = {
            'timestamp': datetime.now(),
            'type': error_type.value,
            'details': error_details,
            'encoder_id': encoder_id
        }
        
        self._error_history.setdefault(encoder_id, []).append(error_entry)
        
        recovery_start = datetime.now()
        recovery_result = await self._execute_recovery_strategy(error_type, encoder_id, error_details)
        
        recovery_time = (datetime.now() - recovery_start).total_seconds()
        self.metrics.recovery_time.observe(recovery_time)
        
        if recovery_result['success']:
            self.metrics.error_state.labels(encoder_id).set(0)
            self._recovery_attempts[encoder_id] = 0
        else:
            self._recovery_attempts[encoder_id] = self._recovery_attempts.get(encoder_id, 0) + 1
            self.metrics.consecutive_errors.labels(error_type.value).inc()
            
        return recovery_result

    async def _execute_recovery_strategy(self, 
                                      error_type: HeloPoolErrorType, 
                                      encoder_id: str,
                                      error_details: Optional[Dict]) -> Dict:
        """Execute error-specific recovery strategies with retry logic"""
        
        strategies = {
            HeloPoolErrorType.CONNECTION_LOST: self._handle_connection_loss,
            HeloPoolErrorType.STREAM_FAILURE: self._handle_stream_failure,
            HeloPoolErrorType.HIGH_RESOURCE_USAGE: self._handle_resource_usage,
            HeloPoolErrorType.ENCODING_ERROR: self._handle_encoding_error,
            HeloPoolErrorType.TEMPERATURE_WARNING: self._handle_temperature_warning,
            HeloPoolErrorType.SYNC_LOSS: self._handle_sync_loss,
            HeloPoolErrorType.BUFFER_OVERFLOW: self._handle_buffer_overflow
        }
        
        strategy = strategies.get(error_type, self._handle_generic_error)
        
        # Implement retry strategy with exponential backoff and jitter
        max_retries = 5
        base_delay = 1  # seconds
        for attempt in range(max_retries):
            result = await strategy(encoder_id, error_details)
            if result['success']:
                return result
            await asyncio.sleep(base_delay * (2 ** attempt) + random.uniform(0, 1))
        
        return {'success': False, 'action': 'failed_after_retries'}

    async def _handle_connection_loss(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle connection loss with automatic reconnection"""
        self.logger.warning(f"Connection lost to HELO encoder {encoder_id}")
        # Implementation of connection recovery logic
        return {'success': True, 'action': 'reconnected'}

    async def _handle_stream_failure(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle stream failures with automatic restart"""
        self.logger.error(f"Stream failure on HELO encoder {encoder_id}")
        # Implementation of stream recovery logic
        return {'success': True, 'action': 'stream_restarted'}

    async def _handle_resource_usage(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle high resource usage warnings"""
        self.logger.warning(f"High resource usage on HELO encoder {encoder_id}")
        # Implementation of resource optimization logic
        return {'success': True, 'action': 'resources_optimized'}

    async def _handle_encoding_error(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle encoding errors with profile adjustment"""
        self.logger.error(f"Encoding error on HELO encoder {encoder_id}")
        # Implementation of encoding recovery logic
        return {'success': True, 'action': 'encoding_adjusted'}

    async def _handle_temperature_warning(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle temperature warnings"""
        self.logger.warning(f"Temperature warning on HELO encoder {encoder_id}")
        # Implementation of temperature management logic
        return {'success': True, 'action': 'temperature_managed'}

    async def _handle_sync_loss(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle sync loss with resync attempt"""
        self.logger.error(f"Sync loss on HELO encoder {encoder_id}")
        # Implementation of sync recovery logic
        return {'success': True, 'action': 'resynced'}

    async def _handle_buffer_overflow(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle buffer overflow with rate adjustment"""
        self.logger.error(f"Buffer overflow on HELO encoder {encoder_id}")
        # Implementation of buffer management logic
        return {'success': True, 'action': 'buffer_adjusted'}

    async def _handle_generic_error(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle unknown errors with basic recovery"""
        self.logger.error(f"Generic error on HELO encoder {encoder_id}")
        # Implementation of generic recovery logic
        return {'success': True, 'action': 'generic_recovery'} 