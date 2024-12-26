from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EndpointMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class EndpointDefinition:
    """Defines an encoder endpoint's properties"""
    path: str
    method: EndpointMethod
    description: str
    requires_auth: bool = True
    rate_limit: Optional[str] = "100/minute"
    cache_ttl: Optional[int] = None  # in seconds
    parameters: Dict[str, Any] = None

class EndpointRegistry:
    """Manages encoder endpoint definitions and their registration"""
    
    def __init__(self):
        self._endpoints: Dict[str, EndpointDefinition] = {}
        self._handlers: Dict[str, Callable] = {}

    def register_endpoint(self, 
                         name: str, 
                         endpoint: EndpointDefinition, 
                         handler: Callable) -> None:
        """
        Register a new endpoint with its handler
        
        Args:
            name: Unique identifier for the endpoint
            endpoint: EndpointDefinition instance
            handler: Function that handles the endpoint logic
        """
        if name in self._endpoints:
            logger.warning(f"Overwriting existing endpoint: {name}")
            
        self._endpoints[name] = endpoint
        self._handlers[name] = handler
        logger.info(f"Registered endpoint: {name} -> {endpoint.path}")

    def load_endpoints_from_dict(self, endpoints_dict: Dict[str, Dict]) -> None:
        """
        Bulk load endpoints from a dictionary configuration
        
        Args:
            endpoints_dict: Dictionary containing endpoint configurations
        """
        for name, config in endpoints_dict.items():
            try:
                endpoint = EndpointDefinition(
                    path=config['path'],
                    method=EndpointMethod[config['method'].upper()],
                    description=config.get('description', ''),
                    requires_auth=config.get('requires_auth', True),
                    rate_limit=config.get('rate_limit'),
                    cache_ttl=config.get('cache_ttl'),
                    parameters=config.get('parameters')
                )
                self._endpoints[name] = endpoint
                logger.info(f"Loaded endpoint configuration: {name}")
            except Exception as e:
                logger.error(f"Failed to load endpoint {name}: {str(e)}")

    def get_endpoint(self, name: str) -> Optional[EndpointDefinition]:
        """Retrieve endpoint definition by name"""
        return self._endpoints.get(name)

    def get_handler(self, name: str) -> Optional[Callable]:
        """Retrieve endpoint handler by name"""
        return self._handlers.get(name)

    def list_endpoints(self) -> Dict[str, EndpointDefinition]:
        """Return all registered endpoints"""
        return self._endpoints.copy()

    def register_with_flask(self, app) -> None:
        """
        Register all endpoints with a Flask application
        
        Args:
            app: Flask application instance
        """
        from flask import request, jsonify
        from functools import wraps
        
        def create_endpoint_handler(endpoint_name: str, endpoint: EndpointDefinition):
            handler = self._handlers.get(endpoint_name)
            
            @wraps(handler)
            def wrapper(*args, **kwargs):
                try:
                    # Add any pre-processing here (auth, validation, etc.)
                    if endpoint.requires_auth:
                        # Implement your auth check here
                        pass
                    
                    # Call the actual handler
                    result = handler(*args, **kwargs)
                    
                    return jsonify(result)
                except Exception as e:
                    logger.error(f"Error in endpoint {endpoint_name}: {str(e)}")
                    return jsonify({"error": str(e)}), 500
            
            return wrapper

        # Register each endpoint with Flask
        for name, endpoint in self._endpoints.items():
            if handler := self._handlers.get(name):
                app.add_url_rule(
                    endpoint.path,
                    f"endpoint_{name}",
                    create_endpoint_handler(name, endpoint),
                    methods=[endpoint.method.value]
                )
                logger.info(f"Registered Flask route: {endpoint.method.value} {endpoint.path}") 