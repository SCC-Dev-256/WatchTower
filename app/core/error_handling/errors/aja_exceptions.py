from typing import Optional, Dict
from datetime import datetime

class AJAClientError(Exception):
    """Base exception for AJA HELO client errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 details: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class AJAConnectionError(AJAClientError):
    """Raised when connection to HELO device fails"""
    pass

class AJAConfigurationError(AJAClientError):
    """Raised when configuration validation fails"""
    pass

class AJAOperationError(AJAClientError):
    """Raised when device operation fails"""
    pass

class AJAStreamError(AJAClientError):
    """Raised when streaming operation fails"""
    pass

class AJARecordError(AJAClientError):
    """Raised when recording operation fails"""
    pass 