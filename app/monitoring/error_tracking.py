import logging
from datetime import datetime
from functools import wraps
from flask import current_app, request, jsonify
from .alert_history import AlertHistory

class ErrorTracker:
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger('error_tracker')
        self.alert_history = AlertHistory()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging handlers"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler for errors
        error_handler = logging.FileHandler('logs/errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # File handler for critical issues
        critical_handler = logging.FileHandler('logs/critical.log')
        critical_handler.setLevel(logging.CRITICAL)
        critical_handler.setFormatter(formatter)
        
        self.logger.addHandler(error_handler)
        self.logger.addHandler(critical_handler)
    
    def track_error(self, error, context=None):
        """Track an error with context"""
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'endpoint': request.endpoint,
            'method': request.method,
            'ip': request.remote_addr,
            'context': context or {}
        }
        
        # Log the error
        self.logger.error(error_data)
        
        # Record in alert history if it's an encoder-related error
        if 'encoder_name' in context:
            self.alert_history.record_alert({
                'encoder_name': context['encoder_name'],
                'alert_type': 'error',
                'severity': 'error',
                'description': str(error),
                'mitigation_steps': context.get('mitigation_steps', [])
            })
        
        # Publish to event system
        if hasattr(self.app, 'encoder_events'):
            self.app.encoder_events.publish_status_change(
                'system',
                {'type': 'error', 'data': error_data}
            )