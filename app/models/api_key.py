from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from app.core.database import Base

class APIKey(Base):
    """API Key model for authentication"""
    __tablename__ = 'api_keys'

    key = Column(String(64), primary_key=True)
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
