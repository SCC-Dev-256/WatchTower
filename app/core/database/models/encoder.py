from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.enums import EncoderStatus, StreamingState, EventType, RecordingFormat
from app.core.database.models.mixins import TimestampMixin, MetricsMixin

class HeloEncoder(db.Model, TimestampMixin):
    __tablename__ = 'encoders'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    ip_address = Column(String(15), unique=True, nullable=False)
    status = Column(Enum(EncoderStatus), default=EncoderStatus.UNKNOWN)
    streaming_state = Column(Enum(StreamingState), default=StreamingState.IDLE)
    recording_state = Column(Boolean, default=False)
    last_checked = Column(DateTime, default=datetime.utcnow)
    firmware_version = Column(String(50))

    def to_dict(self):
        return {
            **super().to_dict(),
            'id': self.id,
            'name': self.name,
            'ip_address': self.ip_address,
            'status': self.status.value,
            'streaming_state': self.streaming_state.value,
            'recording_state': self.recording_state,
            'last_checked': self.last_checked.isoformat(),
            'firmware_version': self.firmware_version
        }

    # Relationships
    metrics = relationship('EncoderMetrics', back_populates='encoder', cascade='all, delete-orphan')
    events = relationship('EncoderEvent', back_populates='encoder', cascade='all, delete-orphan')
    config = relationship('EncoderConfig', back_populates='encoder', uselist=False, cascade='all, delete-orphan')

class EncoderMetrics(db.Model, MetricsMixin):
    __tablename__ = 'encoder_metrics'

    id = Column(Integer, primary_key=True)
    encoder_id = Column(Integer, ForeignKey('encoders.id', ondelete='CASCADE'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    bandwidth_usage = Column(Float)
    stream_health = Column(Float)
    bitrate = Column(Float)
    frame_drops = Column(Integer, default=0)

    encoder = relationship('HeloEncoder', back_populates='metrics')

class EncoderEvent(db.Model):
    __tablename__ = 'encoder_events'

    id = Column(Integer, primary_key=True)
    encoder_id = Column(Integer, ForeignKey('encoders.id', ondelete='CASCADE'))
    event_type = Column(Enum(EventType))
    message = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(db.JSON)

    encoder = relationship('HeloEncoder', back_populates='events')

class EncoderConfig(db.Model):
    __tablename__ = 'encoder_configs'

    id = Column(Integer, primary_key=True)
    encoder_id = Column(Integer, ForeignKey('encoders.id', ondelete='CASCADE'))
    resolution = Column(String(15))
    framerate = Column(Integer)
    bitrate = Column(Integer)
    keyframe_interval = Column(Integer)
    recording_format = Column(Enum(RecordingFormat), default=RecordingFormat.MP4)
    audio_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    encoder = relationship('HeloEncoder', back_populates='config')