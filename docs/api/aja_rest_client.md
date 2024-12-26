# AJA HELO REST API Client

## Overview

The AJA REST API client provides a Python interface for interacting with HELO encoders. It handles device communication, status monitoring, and control operations.

## Usage

### Basic Setup
```python
from app.core.rest_API_client import AJADevice

# Initialize device connection
device = AJADevice("http://192.168.1.100")

# With custom timeout
device = AJADevice("http://192.168.1.100", timeout=30)
```

### System Status
```python
# Get comprehensive system status
status = await device.get_system_status()
print(f"CPU Usage: {status['cpu_usage']}%")
print(f"Temperature: {status['temperature']}°C")
print(f"Fan Speed: {status['fan_speed']} RPM")

# Get specific parameters
stream_state = await device.get_param("eParamID_ReplicatorStreamState")
bitrate = await device.get_param("eParamID_ReplicatorBitrate")
```

### Streaming Control
```python
# Start streaming
await device.set_param("eParamID_ReplicatorStreamState", 1)

# Stop streaming
await device.set_param("eParamID_ReplicatorStreamState", 0)

# Configure stream settings
await device.set_param("eParamID_ReplicatorBitrate", 5000000)  # 5 Mbps
await device.set_param("eParamID_ReplicatorFormat", "1920x1080p30")
```

### Error Handling
```python
try:
    status = await device.get_system_status()
except ConnectionError as e:
    logger.error(f"Connection failed: {str(e)}")
except TimeoutError as e:
    logger.error(f"Request timed out: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

## API Parameters

### System Parameters
- `eParamID_SystemStatus`: Overall system status
- `eParamID_Temperature`: Device temperature
- `eParamID_FanSpeed`: Cooling fan speed
- `eParamID_CPUUsage`: CPU utilization
- `eParamID_MemoryUsage`: Memory usage

### Streaming Parameters
- `eParamID_ReplicatorStreamState`: Streaming state (0=stopped, 1=starting, 2=active)
- `eParamID_ReplicatorBitrate`: Stream bitrate in bps
- `eParamID_ReplicatorFormat`: Video format (e.g., "1920x1080p30")

### Recording Parameters
- `eParamID_ReplicatorRecordState`: Recording state
- `eParamID_StorageSpace`: Available storage
- `eParamID_RecordingName`: Current recording name

## Integration Examples

### Health Monitoring
```python
async def monitor_device_health(device: AJADevice):
    while True:
        try:
            status = await device.get_system_status()
            
            # Check temperature
            if status['temperature'] > 80:
                logger.warning("High temperature detected")
                
            # Check streaming
            stream_state = await device.get_param("eParamID_ReplicatorStreamState")
            if stream_state["value"] != 2:
                logger.error("Stream not active")
                
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            await asyncio.sleep(5)
```

### Automatic Recovery
```python
async def handle_stream_failure(device: AJADevice):
    try:
        # Stop current stream
        await device.set_param("eParamID_ReplicatorStreamState", 0)
        await asyncio.sleep(5)
        
        # Restart stream
        await device.set_param("eParamID_ReplicatorStreamState", 1)
        
        # Verify stream started
        stream_state = await device.get_param("eParamID_ReplicatorStreamState")
        return stream_state["value"] == 2
        
    except Exception as e:
        logger.error(f"Recovery failed: {str(e)}")
        return False
```

## Best Practices

1. Error Handling
- Always implement proper error handling
- Use appropriate timeouts
- Handle connection failures gracefully
- Log all errors and warnings

2. Performance
- Cache frequently accessed parameters
- Implement rate limiting
- Use connection pooling
- Monitor request latency

3. Monitoring
- Track device temperature
- Monitor stream stability
- Log parameter changes
- Alert on failures

4. Security
- Use HTTPS when available
- Implement authentication
- Validate all parameters
- Sanitize inputs 