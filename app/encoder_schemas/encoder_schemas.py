from pydantic import BaseModel, Field, IPvAnyAddress, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class StreamingState(str, Enum):
    IDLE = "idle"
    STREAMING = "streaming"
    RECORDING = "recording"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class EncoderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    ip_address: IPvAnyAddress
    firmware_version: Optional[str] = None

class EncoderCreate(EncoderBase):
    serial_number: str = Field(..., regex="^[A-Z0-9]{8,}$")
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

class EncoderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, regex="^(online|offline|error)$")
    streaming_state: Optional[bool] = None
    recording_state: Optional[bool] = None

class EncoderResponse(EncoderBase):
    id: int
    status: str
    streaming_state: bool
    recording_state: bool
    last_checked: datetime
    
    class Config:
        orm_mode = True

class EncoderControl(BaseModel):
    action: str = Field(..., regex="^(start_streaming|stop_streaming|start_recording|stop_recording)$")
    parameters: Optional[Dict] = None

class EncoderBatchImport(BaseModel):
    encoders: List[EncoderCreate]
    
    @validator('encoders')
    def validate_batch_size(cls, v):
        if len(v) > 100:  # Maximum batch size
            raise ValueError('Batch size exceeds maximum limit of 100')
        return v 