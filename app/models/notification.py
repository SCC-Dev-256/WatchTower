from datetime import datetime
from app.core.database import db

class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_recipients = db.Column(db.String(500))
    email_critical = db.Column(db.Boolean, default=True)
    email_warnings = db.Column(db.Boolean, default=True)
    email_info = db.Column(db.Boolean, default=False)
    
    telegram_token = db.Column(db.String(100))
    telegram_chat_id = db.Column(db.String(100))
    telegram_critical = db.Column(db.Boolean, default=True)
    telegram_warnings = db.Column(db.Boolean, default=True)
    telegram_info = db.Column(db.Boolean, default=False)

class NotificationRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(500), nullable=False)
    channels = db.Column(db.JSON)
    priority = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow) 