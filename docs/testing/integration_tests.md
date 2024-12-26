# Integration Testing Guide

## Setup

```python
# tests/conftest.py
import pytest
from app import create_app
from app.core.connection.health_checker import ConnectionHealthChecker
from app.core.connection.thermal_manager import ConnectionThermalManager

@pytest.fixture
async def app():
    app = create_app('testing')
    return app

@pytest.fixture
async def health_checker(app):
    return ConnectionHealthChecker(
        thermal_manager=app.thermal_manager,
        db_session=app.db.session,
        redis_client=app.redis_client
    )
```

## Health Monitoring Tests

```python
# tests/test_health_monitoring.py
import pytest
from app.core.rest_API_client import AJADevice

async def test_encoder_health_check(app, health_checker):
    # Setup
    encoder_id = "test_encoder"
    device = AJADevice("http://mock-encoder:80")
    
    # Execute
    health = await health_checker.get_detailed_health(encoder_id)
    
    # Assert
    assert health['status'] == 'healthy'
    assert 'connection_health' in health
    assert 'thermal_status' in health

async def test_thermal_management(app, health_checker):
    # Setup
    encoder_id = "test_encoder"
    
    # Execute
    await app.thermal_manager.start_cooling(
        encoder_id=encoder_id,
        reason='test'
    )
    
    # Assert
    temp = await app.thermal_manager.get_temperature(encoder_id)
    assert temp < app.thermal_manager.thresholds['temperature_high']
```

## API Integration Tests

```python
# tests/test_api_integration.py
import pytest
from httpx import AsyncClient

async def test_encoder_status_endpoint(app):
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/api/encoders/test_encoder/status',
            headers={'Authorization': 'Bearer test-token'}
        )
        
        assert response.status_code == 200
        assert 'metrics' in response.json()
        assert 'status' in response.json()

async def test_health_monitoring_integration(app):
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Check system health
        health = await client.get('/health/detailed')
        assert health.status_code == 200
        
        # Verify metrics
        metrics = await client.get('/monitoring/metrics')
        assert metrics.status_code == 200
        assert 'helo_connection_health' in metrics.text
```

## Load Testing

```python
# tests/test_load.py
import asyncio
import pytest
from locust import HttpUser, task, between

class EncoderLoadTest(HttpUser):
    wait_time = between(1, 2)
    
    @task
    def get_encoder_status(self):
        self.client.get(
            '/api/encoders/test_encoder/status',
            headers={'Authorization': f'Bearer {self.token}'}
        )
    
    @task
    def check_health(self):
        self.client.get('/health/detailed')
``` 