from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.ext.declarative import declarative_base

# Create the Base class for SQLAlchemy models
Base = declarative_base()

# Initialize SQLAlchemy and Migrate
db = SQLAlchemy()
migrate = Migrate()

# Import models here to avoid circular import issues
# Move imports to the bottom of the file or inside functions if necessary
__all__ = [
    'db',
    'migrate',
    'SessionLocal',
    'get_test_db',
    'test_db'
]

# Import models after defining db and Base
from .models import (
    APIKey,
    Encoder,
    EncoderMetrics,
    EncoderEvent,
    EncoderConfig,
    LogEntry,
    NotificationSettings,
    NotificationRule
) 