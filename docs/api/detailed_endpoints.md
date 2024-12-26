# Detailed API Documentation

## Authentication
All endpoints require Bearer token authentication:
```http
Authorization: Bearer your-api-key
```

## Encoder Endpoints

### Get Encoder Status
```http
GET /api/encoders/{encoder_id}/status
```

Parameters:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| encoder_id | string | Yes | Unique encoder identifier |
| include_metrics | boolean | No | Include detailed metrics |

Response:
```json
{
    "status": "active",
    "timestamp": "2024-01-20T15:30:00Z",
    "metrics": {
        "cpu_usage": 45.2,
        "memory_usage": 62.8,
        "temperature": 72.5,
        "stream_status": {
            "active": true,
            "bitrate": 5000000,
            "dropped_frames": 0
        }
    }
}
```

### Update Encoder Settings
```http
PUT /api/encoders/{encoder_id}/settings
```

Request Body:
```json
{
    "bitrate": 5000000,
    "resolution": "1920x1080",
    "fps": 30,
    "keyframe_interval": 60
}
```

## Health Monitoring

### Get System Health
```http
GET /api/monitoring/health
```

Response:
```json
{
    "status": "healthy",
    "components": {
        "database": {"status": "healthy"},
        "redis": {"status": "healthy"},
        "encoders": {
            "total": 5,
            "healthy": 4,
            "warning": 1
        }
    }
}
```

### Get Thermal Status
```http
GET /api/monitoring/thermal/{encoder_id}
```

Response:
```json
{
    "temperature": 75.5,
    "cooling_active": false,
    "load_percentage": 65,
    "thermal_score": 82
}
``` 