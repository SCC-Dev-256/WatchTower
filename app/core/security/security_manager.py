from flask import Flask, current_app
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Centralized security management for the application"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.jwt = None
        self.limiter = None
        self.talisman = None
        
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize security components with Flask application
        
        Args:
            app: Flask application instance
        """
        self.app = app
        
        # Initialize JWT handling
        self._setup_jwt()
        
        # Initialize rate limiting
        self._setup_rate_limiting()
        
        # Initialize SSL/TLS security
        self._setup_ssl()
        
        # Register error handlers
        self._register_error_handlers()
        
        logger.info("Security Manager initialized successfully")

    def _setup_jwt(self) -> None:
        """Configure JWT authentication"""
        self.jwt = JWTManager(self.app)
        
        # Ensure JWT secret key is set
        if not self.app.config.get('JWT_SECRET_KEY'):
            raise ValueError("JWT_SECRET_KEY must be set in application config")

    def _setup_rate_limiting(self) -> None:
        """Configure API rate limiting"""
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["100 per minute"],
            storage_uri=self.app.config.get('REDIS_URL')
        )

    def _setup_ssl(self) -> None:
        """Configure SSL/TLS security settings"""
        self.talisman = Talisman(
            self.app,
            force_https=self.app.config.get('FORCE_HTTPS', True),
            session_cookie_secure=True,
            content_security_policy={
                'default-src': "'self'",
                'img-src': "'self' data:",
                'script-src': "'self'",
                'style-src': "'self' 'unsafe-inline'"
            },
            strict_transport_security=True,
            strict_transport_security_max_age=31536000
        )

    def _register_error_handlers(self) -> None:
        """Register security-related error handlers"""
        @self.jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_data):
            return {
                'status': 401,
                'message': 'Token has expired'
            }, 401

        @self.jwt.invalid_token_loader
        def invalid_token_callback(error_string):
            return {
                'status': 401,
                'message': 'Invalid token'
            }, 401

        @self.limiter.request_over_limit
        def ratelimit_handler(e):
            return {
                'status': 429,
                'message': 'Rate limit exceeded'
            }, 429

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key against configured value
        
        Args:
            api_key: API key to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return api_key == self.app.config.get('API_KEY')

    def get_rate_limiter(self) -> Limiter:
        """Get rate limiter instance
        
        Returns:
            Limiter: Flask-Limiter instance
        """
        return self.limiter

    def get_jwt_manager(self) -> JWTManager:
        """Get JWT manager instance
        
        Returns:
            JWTManager: Flask-JWT-Extended instance
        """
        return self.jwt 