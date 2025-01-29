from flask import Flask
from flask_cors import CORS
from .webhooks import webhooks_bp
from .encoder_operations import encoder_ops_bp
from .routes import encoder_bp, monitoring_bp
from .versioning import api_version
from .websocket import init_websocket

__all__ = [
    'init_api',
    'webhooks_bp',
    'encoder_ops_bp',
    'encoder_bp',
    'monitoring_bp',
    'api_version',
    'init_websocket'
]

def init_api(app: Flask):
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['ALLOWED_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register API blueprints
    app.register_blueprint(webhooks_bp, url_prefix='/api/v1')
    app.register_blueprint(encoder_ops_bp, url_prefix='/api/v1')
    app.register_blueprint(encoder_bp, url_prefix='/api/encoders')
    app.register_blueprint(monitoring_bp, url_prefix='/api/monitoring')
    
    return app
