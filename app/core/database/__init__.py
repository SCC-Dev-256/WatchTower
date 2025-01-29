from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
from .session import SessionLocal
from .utils import get_test_db, test_db

db = SQLAlchemy()
migrate = Migrate()

__all__ = [
    'db',
    'migrate',
    'APIKey',
    'Encoder',
    'EncoderMetrics',
    'EncoderEvent',
    'EncoderConfig',
    'LogEntry',
    'NotificationSettings',
    'NotificationRule',
    'SessionLocal',
    'get_test_db',
    'test_db'
] 