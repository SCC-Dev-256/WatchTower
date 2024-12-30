from functools import wraps
from typing import Callable, Any
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)

class RetryConfig:
    def __init__(self, max_attempts: int = 3, delay_seconds: int = 5):
        self.max_attempts = max_attempts
        self.delay_seconds = delay_seconds

class CertificateErrorRecovery:
    def __init__(self, app=None):
        self.app = app
        self.retry_config = RetryConfig()
        self.recovery_history = {}

def error_recovery(operation: str):
    """Decorator for operations that require error recovery. Retries the operation up to a specified number of attempts."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            recovery = CertificateErrorRecovery()
            attempt = 0
            
            logger.info(f"Starting recovery process for operation: {operation}")
            
            while attempt < recovery.retry_config.max_attempts:
                try:
                    logger.debug(f"Attempt {attempt + 1} for operation: {operation}")
                    result = await func(*args, **kwargs)
                    logger.info(f"Recovery successful for operation: {operation} on attempt {attempt + 1}")
                    return result
                except Exception as e:
                    attempt += 1
                    logger.warning(f"{operation} failed (attempt {attempt}): {str(e)}")
                    if attempt == recovery.retry_config.max_attempts:
                        logger.error(f"Recovery failed for operation: {operation} after {attempt} attempts")
                        raise
                    logger.info(f"Retrying operation: {operation} in {recovery.retry_config.delay_seconds} seconds...")
                    await asyncio.sleep(recovery.retry_config.delay_seconds)
            
            logger.info(f"Ending recovery process for operation: {operation}")
            return None
        return wrapper
    return decorator 