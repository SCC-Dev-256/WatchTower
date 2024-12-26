# Thermal Management System

## Overview

The thermal management system prevents encoder overload through proactive monitoring and graduated cooling procedures.

## Components

### 1. Temperature Monitoring

```python
class ConnectionThermalMetrics:
    connection_temperature = Gauge('helo_connection_temperature', 
                                 'Connection temperature score', 
                                 ['encoder_id', 'connection_id'])
    cooling_events = Counter('helo_cooling_events_total', 
                           'Number of cooling events', 
                           ['encoder_id', 'reason'])
```

### 2. Cooling Procedures

```python
async def handle_high_temperature(encoder_id: str):
    # Start gradual cooling
    await thermal_manager.start_cooling(
        encoder_id=encoder_id,
        connection_id=active_connection,
        reason='high_temperature'
    )
    
    # Monitor cooling progress
    while await thermal_manager.check_temperature(encoder_id):
        await asyncio.sleep(30)
```

### 3. Load Management

- Gradual load reduction
- Connection pooling
- Automatic failover
- Warmup scheduling

## API Endpoints

```http
GET /api/monitoring/thermal/status
GET /api/monitoring/thermal/{encoder_id}/temperature
POST /api/monitoring/thermal/{encoder_id}/cooldown
```

## Configuration

```python
THERMAL_CONFIG = {
    'temperature_high': 80,    # °C
    'load_high': 75,          # %
    'burst_limit': 100,       # requests
    'cooling_period': 60,     # seconds
    'gradual_cooldown': 5     # steps
}
``` 