from typing import Dict, Optional
import logging
from datetime import datetime
from prometheus_client import Counter

class LoggingSystem:
    """Handles logging for the application."""
    
    def __init__(self, app=None):
        self.app = app
        # Initialize logging configuration here

    def log_event(self, category: str, event: str, level: str, **kwargs):
        """Log an event with the specified details."""
        # Set up metrics
        self.audit_counter = Counter('audit_events_total', 'Total audit events', ['category', 'level'])
        
        # Format timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Create audit log entry
        audit_entry = {
            'timestamp': timestamp,
            'category': category,
            'event': event,
            'level': level,
            'details': kwargs
        }
        
        # Log based on category
        if category in ['security', 'auth', 'roles']:
            # Security/auth changes
            logging.getLogger('security').info(
                f"Security Event: {event}",
                extra={'audit_entry': audit_entry}
            )
            
        elif category in ['encoder', 'operations']:
            # Encoder operations
            logging.getLogger('encoder').info(
                f"Encoder Event: {event}", 
                extra={'audit_entry': audit_entry}
            )
            
        # Increment metrics counter
        self.audit_counter.labels(
            category=category,
            level=level
        ).inc()
        print(f"[{level.upper()}] {category}: {event} - {kwargs}") 