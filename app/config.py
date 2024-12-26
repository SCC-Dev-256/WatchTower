import os
from pathlib import Path

class BaseConfig:
    # Common configuration
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    SESSION_COOKIE_SECURE = True
    
    # API Settings
    API_KEY_EXPIRY_DAYS = int(os.getenv('API_KEY_EXPIRY_DAYS', '30'))

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    
# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])

class Config(BaseConfig):
    # Existing config...
    
    # Webhook configuration
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    WEBHOOK_RETRY_ATTEMPTS = 3
    WEBHOOK_RETRY_DELAY = 60  # seconds
    
    # CORS configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    
    # API versioning
    CURRENT_API_VERSION = '1.0'
    SUPPORTED_API_VERSIONS = ['1.0', '1.1']
    
    # Certificate monitoring
    CERT_CHECK_INTERVAL = 86400  # 24 hours
    CERT_RENEWAL_THRESHOLD = 30  # days
    DOMAIN = 'your-domain.com'
    ADMIN_EMAIL = 'admin@your-domain.com'
    
    # Metrics
    ENABLE_METRICS = True
    
    # SSL/TLS
    SSL_CERT_PATH = '/etc/letsencrypt/live/your-domain/fullchain.pem'
    SSL_KEY_PATH = '/etc/letsencrypt/live/your-domain/privkey.pem'