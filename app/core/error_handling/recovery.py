from functools import wraps
from typing import Callable, Any, Dict
from datetime import datetime, timedelta
import logging

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
    """Decorator for operations that need error recovery"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            recovery = CertificateErrorRecovery()
            attempt = 0
            
            while attempt < recovery.retry_config.max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    logger.warning(f"{operation} failed (attempt {attempt}): {str(e)}")
                    if attempt == recovery.retry_config.max_attempts:
                        raise
            return None
        return wrapper
    return decorator 