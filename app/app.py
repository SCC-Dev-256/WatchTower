from flask import Flask
from flask_socketio import SocketIO
from app.core.database import db, init_db
from app.core.error_handling import (
    ErrorHandler,
    CertificateErrorHandler,
    MonitoringErrorHandler,
    StreamErrorHandler,
    ErrorLogger
)
from app.services.encoder_manager import EncoderManager
from app.services.notification_service import NotificationService
from app.services.websocket.unified_websocket_service import UnifiedWebSocketService
from app.services.websocket.webhook_service import WebhookService
from app.services.websocket.websocket_auth import WebSocketAuthenticator
from app.services.websocket.websocket_rate_limiter import WebSocketRateLimiter
from app.monitoring.cert_manager import CertificateManager
from app.monitoring.health_check import HealthChecker
from app.monitoring import MonitoringSystem
from app.api.routes.encoders import encoder_bp
from app.services.performance_monitor import PerformanceMonitor
from app.services.stream_validator import StreamValidator

def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize database
    db.init_app(app)
    init_db(app)

    # Initialize error handlers
    app.error_handler = ErrorHandler(app)
    app.cert_error_handler = CertificateErrorHandler(app)
    app.monitoring_error_handler = MonitoringErrorHandler(app)
    app.stream_error_handler = StreamErrorHandler(app)
    app.error_logger = ErrorLogger(app)

    # Register error handlers with Flask
    app.register_error_handler(Exception, app.error_handler.handle_error)

    # Initialize services
    app.encoder_manager = EncoderManager(db)
    app.notification_service = NotificationService(SocketIO(app))
    app.webhook_service = WebhookService(app)
    app.websocket_auth = WebSocketAuthenticator(app)
    app.websocket_rate_limiter = WebSocketRateLimiter()
    app.performance_monitor = PerformanceMonitor(app)
    app.stream_validator = StreamValidator(app)

    # Initialize monitoring
    app.certificate_manager = CertificateManager(app)
    app.health_checker = HealthChecker(app.encoder_manager, app.notification_service)
    app.monitoring_system = MonitoringSystem(app)

    # Initialize WebSocket service
    app.unified_websocket_service = UnifiedWebSocketService(SocketIO(app), app)

    # Register blueprints
    app.register_blueprint(encoder_bp)

    return app 