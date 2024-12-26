from enum import Enum

class EncoderStatus(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"

class StreamingState(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    CONNECTING = "connecting"

class EventType(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    STATE_CHANGE = "state_change"
    CONFIGURATION = "configuration"

class RecordingFormat(Enum):
    MP4 = "mp4"
    MOV = "mov"
    MXF = "mxf"
    
class NetworkMode(Enum):
    STANDARD = "standard"
    RESILIENT = "resilient"
    LOW_LATENCY = "low_latency"
 