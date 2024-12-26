from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class EncoderServiceInterface(ABC):
    """Interface for encoder-related services"""
    
    @abstractmethod
    async def get_status(self, encoder_id: str) -> Dict[str, Any]:
        """Get encoder status"""
        pass
    
    @abstractmethod
    async def update_config(self, encoder_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update encoder configuration"""
        pass
    
    @abstractmethod
    async def handle_error(self, encoder_id: str, error: Exception) -> Dict[str, Any]:
        """Handle encoder-specific errors"""
        pass

class MetricsInterface(ABC):
    """Interface for metrics collection"""
    
    @abstractmethod
    async def collect(self, resource_id: str) -> Dict[str, Any]:
        """Collect current metrics"""
        pass
    
    @abstractmethod
    async def get_historical(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get historical metrics"""
        pass 