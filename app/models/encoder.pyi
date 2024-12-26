from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import relationship
from app.core.enums import EncoderStatus, StreamingState, EventType

class Encoder:
    id: int
    name: str
    ip_address: str
    status: EncoderStatus
    streaming_state: StreamingState
    recording_state: bool
    last_checked: datetime
    firmware_version: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    metrics: List['EncoderMetrics']
    events: List['EncoderEvent']
    config: Optional['EncoderConfig']

class EncoderMetrics:
    id: int
    encoder_id: int
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    bandwidth_usage: float
    stream_health: float
    bitrate: float
    frame_drops: int
    
    encoder: Encoder

class EncoderEvent:
    id: int
    encoder_id: int
    event_type: EventType
    message: str
    timestamp: datetime
    details: Optional[dict]
    
    encoder: Encoder

class EncoderConfig:
    id: int
    encoder_id: int
    resolution: str
    framerate: int
    bitrate: int
    keyframe_interval: int
    audio_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    encoder: Encoder 