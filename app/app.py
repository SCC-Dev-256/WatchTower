from flask import Flask
from app.core.database import db, init_db
from app.core.error_handling import (
    ErrorHandler,
    CertificateErrorHandler,
    MonitoringErrorHandler,
    StreamErrorHandler,
    ErrorLogger
)
from app.api.routes.encoders import encoder_bp

def create_app(config_object="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize error handlers
    app.error_handler = ErrorHandler(app)
    app.cert_error_handler = CertificateErrorHandler(app)
    app.monitoring_error_handler = MonitoringErrorHandler(app)
    app.stream_error_handler = StreamErrorHandler(app)
    app.error_logger = ErrorLogger(app)

    # Initialize extensions
    db.init_app(app)
    init_db(app)

    # Register error handlers with Flask
    app.register_error_handler(Exception, app.error_handler.handle_error)

    # Register blueprints
    app.register_blueprint(encoder_bp)

    return app 