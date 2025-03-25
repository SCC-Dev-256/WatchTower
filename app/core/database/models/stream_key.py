from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class StreamKey(Base):
    __tablename__ = 'stream_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default='gen_random_uuid()')
    encoder_id = Column(UUID(as_uuid=True), ForeignKey('encoders.id'))
    name = Column(String(255), nullable=False)
    input_stream_key = Column(String, nullable=False)  # AJA to Watchtower
    output_stream_key = Column(String, nullable=False)  # Watchtower to YouTube
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    encoder = relationship("Encoder", back_populates="stream_keys")
