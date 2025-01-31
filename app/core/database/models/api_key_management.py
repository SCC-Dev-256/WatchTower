from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from app.core.database import Base

class APIKey(Base):
    """API Key model for authentication"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

    @property
    def is_valid(self) -> bool:
        """Check if API key is valid and active"""
        return bool(
            self.key and 
            self.is_active and 
            self.created_at
        )

    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used_at = datetime.utcnow()

    def __repr__(self):
        return f"<APIKey {self.key}>"

    def to_dict(self):
        """Convert APIKey object to dictionary"""
        return {
            'key': self.key,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_active': self.is_active
        }