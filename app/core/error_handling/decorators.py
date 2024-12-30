from functools import wraps
from flask import current_app
from typing import Callable, Any
import asyncio

def unified_error_handler(operation: str, include_analysis: bool = False, max_attempts: int = 3, delay_seconds: int = 5):
    """Unified error handling and recovery decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    current_app.logger.warning(f"{operation} failed (attempt {attempt}): {str(e)}")
                    
                    if include_analysis:
                        analysis = current_app.error_analyzer.analyze_error({
                            'message': str(e),
                            'operation': operation,
                            'context': kwargs
                        })
                        current_app.logger.info(f"Error analysis: {analysis}")
                    
                    if attempt == max_attempts:
                        current_app.logger.error(f"Recovery failed for operation: {operation} after {attempt} attempts")
                        raise
                    
                    current_app.logger.info(f"Retrying operation: {operation} in {delay_seconds} seconds...")
                    await asyncio.sleep(delay_seconds)
            return None
        return wrapper
    return decorator 