from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import timedelta

class ServiceConfig(BaseModel):
    """Base configuration for services"""
    retry_attempts: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=1.0, ge=0)
    timeout: float = Field(default=5.0, ge=0)
    cache_ttl: Optional[int] = Field(default=300, ge=0)
    metrics_retention: timedelta = Field(default=timedelta(days=30))

class EncoderConfig(ServiceConfig):
    """Encoder-specific configuration"""
    stream_buffer_size: int = Field(default=8192, ge=1024)
    health_check_interval: int = Field(default=60, ge=30)
    auto_recovery: bool = Field(default=True)

class MetricsConfig(ServiceConfig):
    """Metrics-specific configuration"""
    collection_interval: int = Field(default=60, ge=30)
    batch_size: int = Field(default=100, ge=1) 