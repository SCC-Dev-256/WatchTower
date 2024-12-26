from typing import Dict, Type
from .base_service import BaseService

class ServiceRegistry:
    """Simple service registry"""
    
    _services: Dict[str, BaseService] = {}
    
    @classmethod
    def register(cls, name: str, service: BaseService) -> None:
        """Register a service instance"""
        cls._services[name] = service
    
    @classmethod
    def get(cls, name: str) -> BaseService:
        """Get a registered service"""
        if name not in cls._services:
            raise KeyError(f"Service not found: {name}")
        return cls._services[name] 