from typing import Dict, Type
from .base_service import BaseService
from .interfaces import EncoderServiceInterface, MetricsInterface
from app.services.encoder_service import EncoderService
from app.services.metrics_service import MetricsService
from app.services.stream_manager import StreamManager
from app.services.notification_service import NotificationService

class ServiceFactory:
    """Factory for creating service instances"""
    
    _instances: Dict[str, BaseService] = {}
    
    @classmethod
    def get_service(cls, service_type: str) -> BaseService:
        """Get or create a service instance"""
        if service_type not in cls._instances:
            cls._instances[service_type] = cls._create_service(service_type)
        return cls._instances[service_type]
    
    @classmethod
    def _create_service(cls, service_type: str) -> BaseService:
        """Create a new service instance"""
        service_map = {
            'encoder': EncoderService,
            'metrics': MetricsService,
            'stream': StreamManager,
            'notification': NotificationService
        }
        
        if service_type not in service_map:
            raise ValueError(f"Unknown service type: {service_type}")
            
        return service_map[service_type]() 