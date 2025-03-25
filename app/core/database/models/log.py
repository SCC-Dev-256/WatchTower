from datetime import datetime
from typing import Dict, Any, Optional, Union
from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database.base import Base
from app.core.enums import EncoderStatus, StreamingState, EventType
from app.core.error_handling.central_error_manager import HeloPoolErrorType
from app.core.error_handling.errors.exceptions import APIError, EncoderError, AJAClientError

class Log(Base):
    """Database model for system logs and error tracking"""
    
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    level = Column(String(20), nullable=False)  # error, warning, info, debug
    source = Column(String(100), nullable=False)  # api, encoder, helo, system, etc.
    error_type = Column(String(100))  # Specific error type from HeloPoolErrorType or custom
    message = Column(String(500), nullable=False)
    details = Column(JSON)  # Additional error context and details
    stack_trace = Column(String)  # Full stack trace if available
    resolution = Column(String(500))  # How the error was resolved
    resolution_time = Column(Float)  # Time taken to resolve in seconds
    
    # Foreign keys for related entities
    encoder_id = Column(String(50), ForeignKey('encoders.id'))
    stream_id = Column(String(50), ForeignKey('streams.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    encoder = relationship("Encoder", back_populates="logs")
    stream = relationship("Stream", back_populates="logs")
    user = relationship("User", back_populates="logs")

    @classmethod
    def from_error(cls, error: Exception, source: str, context: Dict[str, Any] = None) -> 'Log':
        """Create a Log entry from an Exception"""
        error_type = None
        if isinstance(error, APIError):
            error_type = f"api_{error.code}"
        elif isinstance(error, EncoderError):
            error_type = f"encoder_{error.error_type or 'unknown'}"
        elif isinstance(error, AJAClientError):
            error_type = f"aja_{error.error_type or 'unknown'}"
        elif isinstance(error, HeloPoolErrorType):
            error_type = f"helo_{error.value}"

        return cls(
            level='error',
            source=source,
            error_type=error_type,
            message=str(error),
            details=context or {},
            stack_trace=getattr(error, '__traceback__', None)
        )

    @classmethod
    def from_state_change(cls, 
                         service: str,
                         entity_id: str,
                         old_state: Union[EncoderStatus, StreamingState],
                         new_state: Union[EncoderStatus, StreamingState],
                         details: Optional[Dict] = None) -> 'Log':
        """Create a Log entry from a state change"""
        return cls(
            level='info',
            source=service,
            error_type='state_change',
            message=f"State changed from {old_state} to {new_state}",
            details={
                'entity_id': entity_id,
                'old_state': str(old_state),
                'new_state': str(new_state),
                **(details or {})
            }
        )

    @classmethod
    def from_security_event(cls,
                          event_type: str,
                          source_ip: str,
                          details: Dict[str, Any],
                          severity: str = 'warning') -> 'Log':
        """Create a Log entry from a security event"""
        return cls(
            level=severity,
            source='security',
            error_type=f"security_{event_type}",
            message=f"Security event: {event_type} from {source_ip}",
            details={
                'source_ip': source_ip,
                **details
            }
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'source': self.source,
            'error_type': self.error_type,
            'message': self.message,
            'details': self.details,
            'stack_trace': self.stack_trace,
            'resolution': self.resolution,
            'resolution_time': self.resolution_time,
            'encoder_id': self.encoder_id,
            'stream_id': self.stream_id,
            'user_id': self.user_id
        }
