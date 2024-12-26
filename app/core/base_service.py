from typing import Optional, Dict, Any
import logging
from flask import current_app
from .error_handling import handle_errors
from .error_handling.exceptions import APIError

class BaseService:
    """Simplified base service with essential functionality"""
    
    def __init__(self, logger_name: Optional[str] = None):
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)
        self.config = current_app.config if current_app else {}

    @handle_errors()
    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute service operation with error handling"""
        method = getattr(self, f"_op_{operation}", None)
        if not method:
            raise APIError(f"Unknown operation: {operation}")
            
        self.logger.info(f"Executing {operation}", extra={"params": kwargs})
        return await method(**kwargs)

    async def _validate_params(self, params: Dict, required: list) -> None:
        """Validate required parameters"""
        missing = [field for field in required if field not in params]
        if missing:
            raise APIError(
                "Missing required parameters",
                details={'missing': missing}
            )