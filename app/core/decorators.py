from functools import wraps
from typing import Dict
import logging
from app.core.error_handling.error_logging import ErrorLogger

logger = logging.getLogger(__name__)

def handle_remediation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Dict:
        try:
            result = await func(*args, **kwargs)
            if isinstance(result, dict) and result.get('actions'):
                logger.info(f"Remediation successful: {result['actions']}")
            return result
        except Exception as e:
            logger.error(f"Remediation failed in {func.__name__}: {str(e)}")
            return {'success': False, 'error': str(e)}
    return wrapper 

def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log the error using ErrorLogger
            ErrorLogger().log_error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper 