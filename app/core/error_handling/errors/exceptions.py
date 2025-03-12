from typing import Dict, Any, Optional
from app.core.aja.aja_constants import ReplicatorCommands
from datetime import datetime


# This file contains the APIError class, which is used to handle API errors.
# The APIError class is a subclass of the Exception class and has the following parameters:
# - message: The error message.
# - code: The HTTP status code.
# - details: Additional details about the error.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `success` and `error` methods.
# - Detailed implementation for methods like `success` and `error`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `success` and `error` methods.


class APIError(Exception):
    """Base API Error"""
    def __init__(self, message: str, code: int = 400, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class ValidationError(APIError):
    """Exception raised for validation errors."""
    def __init__(self, message="Validation error", code=422, error_type: Optional[str] = None, details=None):
        super().__init__(message, code=code, error_type=error_type, details=details)
        self.timestamp = datetime.utcnow()

class NotFoundError(APIError):
    """Exception raised when a resource is not found."""
    def __init__(self, message="Resource not found", code=404, error_type: Optional[str] = None, details=None):
        super().__init__(message, code=code, error_type=error_type, details=details) 
        self.timestamp = datetime.utcnow()

class EncoderError(Exception):
    """Base class for encoder-related errors."""
    def __init__(self, message, encoder_id=None, error_type=None):
        super().__init__(message)
        self.encoder_id = encoder_id
        self.error_type = error_type 
        self.timestamp = datetime.utcnow()

class EncoderStreamError(EncoderError):
    """Exception raised for encoder streaming-related errors."""
    def __init__(self, message: str, encoder_id: Optional[str] = None, error_type: Optional[str] = None):
        super().__init__(message, encoder_id=encoder_id, error_type=error_type)
        self.timestamp = datetime.utcnow()

class LoadBalancerError(Exception):
    """Exception raised for load balancer-related errors."""
    def __init__(self, message: str, encoder_id: Optional[str] = None, error_type: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.encoder_id = encoder_id
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class MonitoringError(Exception):
    """Base class for monitoring-related errors."""
    def __init__(self, message, code=500, error_type: Optional[str] = None, details=None):
        super().__init__(message)
        self.code = code
        self.error_type = error_type
        self.details = details or {} 
        self.timestamp = datetime.utcnow()

class CertificateError(Exception):
    """Base class for certificate-related errors."""
    def __init__(self, message, code=500, error_type: Optional[str] = None,  details=None):
        super().__init__(message)
        self.code = code
        self.error_type = error_type
        self.details = details or {} 
        self.timestamp = datetime.utcnow()


from typing import Optional, Dict
from datetime import datetime

class AJAClientError(Exception):
    """Base exception for AJA HELO client errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, error_type: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class AJAConnectionError(AJAClientError):
    """Raised when connection to HELO device fails due to network or device issues.
    Common scenarios:
    - Network connectivity issues
    - Invalid IP address/hostname
    - Device in DATA_LAN media state instead of RECORD_STREAM"""
    def __init__(self, message: str, status_code: Optional[int] = None, media_state: Optional[int] = None):
        super().__init__(message, status_code=status_code, error_type="connection",
                        details={"media_state": media_state})

class AJAConfigurationError(AJAClientError):
    """Raised when parameter validation fails based on Parameter_Configuration_Table constraints.
    Common scenarios:
    - Invalid parameter values
    - Out of range values for bitrate, framerate etc
    - Invalid enum values"""
    def __init__(self, message: str, param_name: str, invalid_value: Any):
        super().__init__(message, status_code=400, error_type="configuration",
                        details={"parameter": param_name, "invalid_value": invalid_value})

class AJAOperationError(AJAClientError):
    """Raised when device operation fails.
    Common scenarios:
    - Invalid command sequence
    - Device in wrong state for operation
    - Hardware/firmware errors"""
    def __init__(self, message: str, command: Optional[ReplicatorCommands] = None):
        super().__init__(message, status_code=500, error_type="operation",
                        details={"command": command.name if command else None})

class AJAStreamError(AJAClientError):
    """Raised when streaming operation fails.
    Common scenarios:
    - Network bandwidth issues
    - Dropped frames exceeding threshold
    - Invalid streaming profile"""
    def __init__(self, message: str, dropped_frames: Optional[int] = None, 
                 stream_health: Optional[str] = None):
        super().__init__(message, status_code=500, error_type="streaming",
                        details={"dropped_frames": dropped_frames,
                                "stream_health": stream_health})

class AJARecordError(AJAClientError):
    """Raised when recording operation fails.
    Common scenarios:
    - Storage media full/unavailable 
    - Invalid recording profile
    - Dropped frames exceeding threshold"""
    def __init__(self, message: str, media_type: Optional[str] = None,
                 dropped_frames: Optional[int] = None):
        super().__init__(message, status_code=500, error_type="recording",
                        details={"media_type": media_type,
                                "dropped_frames": dropped_frames})