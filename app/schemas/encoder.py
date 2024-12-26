from pydantic import BaseModel, IPvAnyAddress
from typing import Optional
from datetime import datetime

class EncoderSchema(BaseModel):
    name: str
    ip_address: IPvAnyAddress
    status: Optional[str] = "unknown"
    streaming_state: Optional[bool] = False
    recording_state: Optional[bool] = False 