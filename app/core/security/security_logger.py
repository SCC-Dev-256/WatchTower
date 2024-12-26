from flask import request
import logging

class SecurityEventLogger:
    def __init__(self, app):
        self.logger = logging.getLogger('security')
        self.setup_logging(app)
        
    def setup_logging(self, app):
        """Configure security event logging"""
        handler = logging.FileHandler('security_events.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s\n'
            'IP: %(ip_address)s\n'
            'User-Agent: %(user_agent)s\n'
            'Details: %(details)s\n'
            '-' * 80
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.WARNING)
        
        # Add Prometheus metrics
        if app.config.get('ENABLE_METRICS', True):
            from prometheus_client import Counter
            self.security_events = Counter(
                'security_events_total',
                'Security events by type',
                ['event_type', 'severity']
            )
        
    def log_ssl_event(self, event_type: str, details: dict):
        """Log SSL/TLS related security events"""
        self.logger.warning(f"SSL Security Event: {event_type}", extra={
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            **details
        }) 