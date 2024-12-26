from typing import Dict, Any, Optional

class APIError(Exception):
    """Base API Error"""
    def __init__(self, message: str, code: int = 400, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class EncoderError(APIError):
    """Encoder-specific errors"""
    def __init__(self, message: str, encoder_id: str, error_type: str = None):
        details = {"encoder_id": encoder_id}
        if error_type:
            details["error_type"] = error_type
        super().__init__(message, code=400, details=details) 