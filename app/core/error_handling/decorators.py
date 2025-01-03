from functools import wraps
from flask import current_app, jsonify
from typing import Callable, Any
from app.core.error_handling.ErrorLogging import ErrorLogger
from app.core.error_handling.analysis import ErrorAnalyzer
import asyncio

def handle_errors(operation: str, error_type: str = 'api', severity: str = 'error', include_analysis: bool = False, max_attempts: int = 3, delay_seconds: int = 5):
    """Unified error handling and recovery decorator that integrates with ErrorLogger"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    error_data = {
                        'service': operation,
                        'error': str(e),
                        'attempt': attempt,
                        'context': kwargs
                    }
                    
                    # Log using ErrorLogger
                    ErrorLogger.log_error(
                        error_data=error_data,
                        error_type=error_type,
                        severity=severity
                    )
                    
                    if include_analysis:
                        analysis = ErrorAnalyzer.analyze_error({
                            'message': str(e),
                            'operation': operation,
                            'context': kwargs
                        })
                        current_app.error_logger.log_enhanced_error(
                            error_type=error_type,
                            service=operation,
                            resolution_strategy='retry',
                            resolution_time=delay_seconds * attempt
                        )
                    
                    if attempt == max_attempts:
                        current_app.error_logger.log_error(
                            error_data={
                                **error_data,
                                'final_attempt': True
                            },
                            error_type=error_type,
                            severity='critical'
                        )
                        raise
                    
                    await asyncio.sleep(delay_seconds)
            return None
        return wrapper
    return decorator