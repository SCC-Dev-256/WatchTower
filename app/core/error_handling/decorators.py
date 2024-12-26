from functools import wraps
from flask import current_app
from .exceptions import APIError, EncoderError
from typing import Callable, Any

def handle_errors(include_analysis: bool = False):
    """Unified error handling decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except EncoderError as e:
                if include_analysis:
                    analysis = current_app.error_analyzer.analyze_error({
                        'message': str(e),
                        'type': e.details.get('error_type'),
                        'encoder_id': e.details.get('encoder_id'),
                        'context': e.details
                    })
                    e.details['analysis'] = analysis
                return current_app.error_handler.handle_error(e)
            except Exception as e:
                return current_app.error_handler.handle_error(
                    APIError("Internal server error", code=500, details={'error': str(e)})
                )
        return wrapper
    return decorator 