from typing import Dict, Any, Optional
from datetime import datetime
from .config import ServiceConfig
from .error_handling import ErrorHandler

class ServiceContext:
    """Context for service operations"""
    
    def __init__(
        self,
        config: ServiceConfig,
        error_handler: ErrorHandler,
        request_id: Optional[str] = None
    ):
        self.config = config
        self.error_handler = error_handler
        self.request_id = request_id or self._generate_request_id()
        self.start_time = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to context"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata from context"""
        return self.metadata.get(key)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since context creation"""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    @staticmethod
    def _generate_request_id() -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4()) 