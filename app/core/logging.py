import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request
from pythonjsonlogger import jsonlogger
from app.config.config import settings
from datetime import datetime

class RequestFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add request context if available
        if has_request_context():
            log_record.update({
                'ip': request.remote_addr,
                'method': request.method,
                'url': request.url,
                'user_agent': request.user_agent.string
            })
        
        # Add standard fields
        log_record.update({
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'app_name': settings.APP_NAME
        })

def setup_logging(app):
    """Configure application logging"""
    # Create logs directory
    log_dir = Path(app.root_path) / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # Configure formatter
    formatter = RequestFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Configure handlers
    handlers = [
        RotatingFileHandler(
            log_dir / settings.LOG_FILE,
            maxBytes=10485760,  # 10MB
            backupCount=10
        ),
        logging.StreamHandler(sys.stdout)
    ]
    
    # Set formatter for all handlers
    for handler in handlers:
        handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Remove existing handlers and add new ones
    root_logger.handlers = []
    for handler in handlers:
        root_logger.addHandler(handler)

class EncoderLogger:
    def __init__(self, name: str):
        self.logger = setup_logging(name)
        self.context = {}

    def set_context(self, **kwargs):
        """Set context for all subsequent log messages"""
        self.context.update(kwargs)

    def log_encoder_event(self, encoder_id: str, event_type: str, **kwargs):
        """Log encoder-specific events"""
        self.logger.info(
            f"Encoder event: {event_type}",
            extra={
                "encoder_id": encoder_id,
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                **self.context,
                **kwargs
            }
        )

    def log_metric(self, metric_name: str, value: float, **kwargs):
        """Log metrics with standardized format"""
        self.logger.info(
            f"Metric recorded: {metric_name}",
            extra={
                "metric_name": metric_name,
                "value": value,
                "unit": kwargs.get("unit", ""),
                **self.context,
                **kwargs
            }
        )