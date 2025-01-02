from datetime import datetime
from app.core.database import db
from app.core.database.models.mixins import TimestampMixin

class APIKey(db.Model, TimestampMixin):
    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='api_keys')

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }

    def __repr__(self):
        return f"<APIKey {self.key}>"