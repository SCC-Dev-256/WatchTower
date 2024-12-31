from enum import Enum

class ErrorType(Enum):
    # Stream Related
    STREAM_START = "stream_start"
    STREAM_QUALITY = "stream_quality"
    STREAM_CONFIG = "stream_config"
    
    # Connection Related
    CONNECTION_LOST = "connection_lost"
    CONNECTION_TIMEOUT = "connection_timeout"
    NETWORK_CONGESTION = "network_congestion"
    
    # Hardware Related
    STORAGE_FULL = "storage_full"
    CPU_OVERLOAD = "cpu_overload"
    MEMORY_FULL = "memory_full"
    
    # Failover Related
    FAILOVER_TRIGGER = "failover_trigger"
    FAILOVER_CONFIG = "failover_config"
    HANDOFF_FAILED = "handoff_failed"
    
    # System Related
    CONFIG_INVALID = "config_invalid"
    AUTH_FAILED = "auth_failed"
    RESOURCE_NOT_FOUND = "resource_not_found" 