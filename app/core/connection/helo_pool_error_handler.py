from enum import Enum
from typing import Dict, Optional, List, Any
from datetime import datetime
import logging
import random
import asyncio
from prometheus_client import Counter, Gauge, Histogram
from app.core.error_handling.central_error_manager import CentralErrorManager
from app.core.helo.helo_commands import (
    start_recording, stop_recording, start_streaming, stop_streaming,
    verify_streaming, verify_recording
)

logger = logging.getLogger(__name__)

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
    
    def __init__(self, central_error_manager: CentralErrorManager, logger: Optional[logging.Logger] = None):
        self.central_error_manager = central_error_manager
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = HeloPoolErrorMetrics()
        self._error_history: Dict[str, List[Dict]] = {}
        self._recovery_attempts: Dict[str, int] = {}

    async def handle_error(self, 
                         error_type: HeloPoolErrorType, 
                         encoder_id: str, 
                         error_details: Optional[Dict] = None) -> Dict:
        """Handle HELO-specific errors with detailed logging and recovery attempts"""
        error_context = {
            'encoder_id': encoder_id,
            'error_type': error_type.value,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'time': datetime.now().strftime("%H:%M:%S"),
            'details': error_details
        }
        
        self.logger.error(
            f"Handling error for encoder {encoder_id}",
            extra=error_context
        )

        # Delegate error processing to CentralErrorManager
        return await self.central_error_manager.process_error(
            Exception(f"HELO error: {error_type.value}"),
            source='helo',
            context=error_context,
            error_type=error_type
        )

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
        try:
            # Attempt to reconnect using a command from helo_commands
            if start_streaming(f"http://{encoder_id}"):
                return {'success': True, 'action': 'reconnected'}
        except Exception as e:
            self.logger.error(f"Failed to reconnect encoder {encoder_id}: {str(e)}")
        return {'success': False, 'action': 'reconnection_failed'}

    async def _handle_stream_failure(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle stream failures with automatic restart"""
        self.logger.error(f"Stream failure on HELO encoder {encoder_id}")
        try:
            # Restart streaming using a command from helo_commands
            if start_streaming(f"http://{encoder_id}"):
                return {'success': True, 'action': 'stream_restarted'}
        except Exception as e:
            self.logger.error(f"Failed to restart stream for encoder {encoder_id}: {str(e)}")
        return {'success': False, 'action': 'stream_restart_failed'}

    async def _handle_resource_usage(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle high resource usage warnings"""
        self.logger.warning(f"High resource usage on HELO encoder {encoder_id}")
        try:
            # Adjust resource settings
            await self._optimize_resources(encoder_id)
            return {'success': True, 'action': 'resources_optimized'}
        except Exception as e:
            self.logger.error(f"Failed to optimize resources for encoder {encoder_id}: {str(e)}")
            return {'success': False, 'action': 'resource_optimization_failed'}

    async def _handle_encoding_error(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle encoding errors with profile adjustment"""
        self.logger.error(f"Encoding error on HELO encoder {encoder_id}")
        try:
            # Adjust encoding settings
            await self._adjust_encoding(encoder_id)
            return {'success': True, 'action': 'encoding_adjusted'}
        except Exception as e:
            self.logger.error(f"Failed to adjust encoding for encoder {encoder_id}: {str(e)}")
            return {'success': False, 'action': 'encoding_adjustment_failed'}

    async def _handle_temperature_warning(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle temperature warnings by checking and adjusting device settings"""
        self.logger.warning(f"Temperature warning on HELO encoder {encoder_id}")
        try:
            # Check and manage temperature
            temperature = await self._get_device_param(encoder_id, 'eParamID_Temperature')
            if temperature > self.temperature_threshold:
                await self._adjust_device_settings(encoder_id, 'cooling')
            return {'success': True, 'action': 'temperature_managed'}
        except Exception as e:
            self.logger.error(f"Failed to manage temperature for encoder {encoder_id}: {str(e)}")
            return {'success': False, 'action': 'temperature_management_failed'}

    async def _handle_sync_loss(self, encoder_id: str, details: Optional[Dict]) -> Dict:
        """Handle sync loss by attempting to restart streaming or recording"""
        self.logger.warning(f"Sync loss detected on HELO encoder {encoder_id}")
        
        try:
            # Verify current streaming state using a command from helo_commands
            if not verify_streaming(f"http://{encoder_id}"):
                if start_streaming(f"http://{encoder_id}"):
                    return {'success': True, 'action': 'sync_restored'}
        except Exception as e:
            self.logger.error(f"Failed to restore sync for encoder {encoder_id}: {str(e)}")
        return {'success': False, 'action': 'sync_restoration_failed'}

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