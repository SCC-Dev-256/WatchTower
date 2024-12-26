# API Endpoints Documentation

## Health & Monitoring

### Encoder Health
```http
GET /health/encoder/{encoder_id}
```

Response:
```json
{
    "timestamp": "2024-01-20T15:30:00Z",
    "encoder": {
        "device_status": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "temperature": 72.5,
            "fan_speed": 1200,
            "uptime": 345600
        },
        "streaming": {
            "active": true,
            "bitrate": 5000000,
            "format": "1920x1080p30"
        },
        "connection_health": {
            "health_score": 85.5,
            "issues": []
        }
    }
}
```

### System Health
```http
GET /health/detailed
```

Response:
```json
{
    "status": "healthy",
    "timestamp": "2024-01-20T15:30:00Z",
    "system": {
        "cpu_percent": 35.2,
        "memory_used_percent": 68.5,
        "disk_used_percent": 72.1
    },
    "services": {
        "database": {"status": "healthy"},
        "redis": {"status": "healthy"}
    },
    "encoders": {
        "encoder_1": {
            "device_status": {},
            "connection_health": {},
            "thermal_status": {}
        }
    }
}
``` 