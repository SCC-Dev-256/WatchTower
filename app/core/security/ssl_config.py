# config/ssl_config.py
from flask_talisman import Talisman
from dataclasses import dataclass, field
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

@dataclass
class SSLConfig:
    """SSL/TLS Configuration settings for the application"""
    force_https: bool = True
    session_cookie_secure: bool = True
    content_security_policy: Dict[str, List[str]] = field(default_factory=lambda: {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'"],
        "frame-ancestors": ["'none'"],
        "form-action": ["'self'"]
    })
    hsts_max_age: int = 31536000  # 1 year in seconds
    hsts_include_subdomains: bool = True
    hsts_preload: bool = True
    referrer_policy: str = "strict-origin-when-cross-origin"
    public_key_pins: Dict[str, str] = field(default_factory=lambda: {
        "pin-sha256": [
            "base64+primary==",
            "base64+backup=="
        ],
        "max-age": "2592000",  # 30 days
        "includeSubDomains": True
    })

def configure_ssl(app, config: SSLConfig = SSLConfig()):
    """
    Configure SSL/TLS security for the Flask app
    
    Args:
        app: Flask application instance
        config: SSLConfig instance with security settings
    """
    try:
        Talisman(app,
            force_https=config.force_https,
            session_cookie_secure=config.session_cookie_secure,
            content_security_policy=config.content_security_policy,
            strict_transport_security=True,
            strict_transport_security_max_age=config.hsts_max_age,
            strict_transport_security_include_subdomains=config.hsts_include_subdomains,
            strict_transport_security_preload=config.hsts_preload,
            referrer_policy=config.referrer_policy,
            force_file_save=True,
            frame_options='DENY',
            feature_policy={
                'geolocation': "'none'",
                'microphone': "'none'",
                'camera': "'none'",
                'payment': "'none'",
                'usb': "'none'"
            },
            force_https_permanent=True,
            public_key_pins=config.public_key_pins
        )
        # Additional security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Permissions-Policy'] = 'interest-cohort=()'
            return response

        logger.info("SSL/TLS security configuration applied successfully")
    except Exception as e:
        logger.error(f"Failed to configure SSL/TLS security: {str(e)}")
        raise