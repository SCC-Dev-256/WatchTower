import os
from dotenv import load_dotenv

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        load_dotenv()  # Load environment variables from a .env file if present
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret')
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
        self.WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'default_webhook_secret')
        self.MAX_WEBSOCKET_CLIENTS = int(os.getenv('MAX_WEBSOCKET_CLIENTS', 100))
        self.PROMETHEUS_ENABLED = os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true'
        # Add more configuration settings as needed

    def get(self, key, default=None):
        return getattr(self, key, default)

# Usage
config = Config() 