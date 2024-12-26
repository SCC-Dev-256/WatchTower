from typing import Dict, Any
from flask import jsonify
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API Error"""
    def __init__(self, message: str, code: int = 400, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class NotFoundError(APIError):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found", details: Dict[str, Any] = None):
        super().__init__(message, code=404, details=details)

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message: str = "Validation error", details: Dict[str, Any] = None):
        super().__init__(message, code=422, details=details)

class EncoderError(APIError):
    """Encoder-specific errors"""
    def __init__(self, message: str, encoder_id: str = None, **kwargs):
        details = {"encoder_id": encoder_id, **kwargs}
        super().__init__(message, code=400, details=details)

class StreamError(EncoderError):
    """Streaming-related errors"""
    pass

class ConfigurationError(EncoderError):
    """Configuration-related errors"""
    pass

def handle_api_error(error: APIError):
    """Handle API errors"""
    response = {
        "error": error.message,
        "code": error.code,
        "details": error.details
    }
    logger.error(f"API Error: {error.message}", extra={"details": error.details})
    return jsonify(response), error.code

def setup_error_handlers(app):
    """Register error handlers"""
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(404, lambda e: handle_api_error(NotFoundError()))
    app.register_error_handler(500, lambda e: handle_api_error(
        APIError("Internal server error", code=500)
    )) 

def error_handler(func):
    """Unified error handling decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise APIError("Validation failed", code=422, details=e.errors())
        except EncoderError as e:
            raise
        except Exception as e:
            logger.exception("Unexpected error")
            raise APIError("Internal server error", code=500)
    return wrapper 