import logging

class SecurityEventLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        self.setup_logging()

    def setup_logging(self):
        handler = logging.FileHandler('security_events.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, details: dict):
        self.logger.info(f"Security Event: {event_type}", extra=details) 