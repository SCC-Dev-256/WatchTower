from pydantic import BaseSettings, PostgresDsn, SecretStr, validator
from typing import Optional, Dict
import os

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Encoder Manager API"
    DEBUG: bool = False
    SECRET_KEY: SecretStr
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "encoder_db")
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "app.log"
    
    # Security Settings
    JWT_SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list = ["*"]
    
    # Rate Limiting
    RATELIMIT_DEFAULT: str = "100/minute"
    RATELIMIT_STORAGE_URL: str = "redis://localhost:6379/0"
    
    # Add encoder-specific settings
    ENCODER_DEFAULTS = {
        "MAX_BATCH_SIZE": 100,
        "STREAM_BITRATE_LIMIT": 20000000,
        "HEALTH_CHECK_INTERVAL": 60,
        "RETRY_ATTEMPTS": 3
    }
    
    # Add validation rules
    VALIDATION_RULES = {
        "name_max_length": 100,
        "serial_number_pattern": "^[A-Z0-9]{8,}$",
        "ip_range": "192.168.0.0/16"
    }
    
    # Add monitoring thresholds
    MONITORING = {
        "cpu_threshold": 80.0,
        "memory_threshold": 85.0,
        "stream_health_minimum": 95.0
    }
    
    # Add WebSocket settings
    WEBSOCKET = {
        "ping_interval": 25,
        "ping_timeout": 120,
        "max_clients": 1000,
        "batch_size": 50
    }
    
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 