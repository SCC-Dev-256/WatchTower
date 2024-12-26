from functools import wraps
from typing import Dict
import logging

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