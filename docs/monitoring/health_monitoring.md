# Health Monitoring System

## Overview

The health monitoring system provides comprehensive monitoring of HELO encoders through multiple layers:
- Direct device monitoring via AJA REST API
- Connection health tracking
- Thermal management
- System-level metrics

## Components

### 1. Direct Device Monitoring

```python
from app.core.rest_API_client import AJADevice
from app.core.connection.health_checker import ConnectionHealthChecker

async def monitor_device(encoder_id: str):
    device = AJADevice(f"http://{encoder.ip_address}")
    health_checker = ConnectionHealthChecker(
        thermal_manager=current_app.thermal_manager,
        db_session=current_app.db.session,
        redis_client=current_app.redis_client
    )
    
    # Get comprehensive health status
    status = await health_checker.get_detailed_health(encoder_id)
    
    # Check critical metrics
    if status['device_status']['temperature'] > 80:
        await handle_high_temperature(encoder_id)
        
    if status['connection_health']['health_score'] < 70:
        await handle_degraded_connection(encoder_id)
```

### 2. Metrics Collection

```python
# Prometheus metrics
health_score = Gauge('helo_connection_health', 
                    'Connection health score', 
                    ['encoder_id', 'connection_id'])
health_checks = Counter('helo_health_checks_total', 
                       'Number of health checks', 
                       ['encoder_id', 'result'])
check_duration = Histogram('helo_check_duration_seconds', 
                          'Health check duration')
```

### 3. Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU Usage | 80% | 90% | Scale/Cooldown |
| Temperature | 75°C | 85°C | Thermal Management |
| Memory | 85% | 95% | Resource Recovery |
| Health Score | 70 | 50 | Connection Reset |

## API Endpoints

### Health Status
```http
GET /health/encoder/{encoder_id}
GET /health/detailed
```

### Metrics
```http
GET /monitoring/metrics
GET /monitoring/alerts
```

## Integration Examples

### WebSocket Monitoring
```python
@sio.on('health_update')
def on_health_update(data):
    # Process real-time health updates
    if data['health_score'] < threshold:
        notify_operators(data)
    
    # Update dashboards
    update_grafana_dashboard(data)
```

### Automated Recovery
```python
async def handle_degraded_health(encoder_id: str):
    # Get current health status
    health = await health_checker.get_detailed_health(encoder_id)
    
    # Implement recovery steps
    if health['connection_health']['health_score'] < 50:
        await reset_connection(encoder_id)
    elif health['thermal_status']['temperature'] > 80:
        await start_cooling_procedure(encoder_id)
``` 