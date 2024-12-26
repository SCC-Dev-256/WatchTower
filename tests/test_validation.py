import pytest
from app.schemas.encoder_schemas import EncoderCreate, EncoderControl
from pydantic import ValidationError

def test_encoder_create_validation():
    # Valid data
    valid_data = {
        "name": "Test Encoder",
        "ip_address": "192.168.1.100",
        "serial_number": "ABC123456",
        "firmware_version": "1.0.0"
    }
    encoder = EncoderCreate(**valid_data)
    assert encoder.name == "Test Encoder"
    
    # Invalid IP
    with pytest.raises(ValidationError):
        EncoderCreate(
            name="Test",
            ip_address="invalid_ip",
            serial_number="ABC123456"
        )
    
    # Invalid serial number
    with pytest.raises(ValidationError):
        EncoderCreate(
            name="Test",
            ip_address="192.168.1.100",
            serial_number="123"  # Too short
        )

def test_encoder_control_validation():
    # Valid action
    valid_data = {
        "action": "start_streaming",
        "parameters": {"quality": "high"}
    }
    control = EncoderControl(**valid_data)
    assert control.action == "start_streaming"
    
    # Invalid action
    with pytest.raises(ValidationError):
        EncoderControl(
            action="invalid_action",
            parameters={}
        )

@pytest.mark.asyncio
async def test_encoder_endpoint_validation(client):
    # Test invalid data
    response = await client.post("/api/encoders", json={
        "name": "",  # Invalid empty name
        "ip_address": "invalid_ip",
        "serial_number": "123"
    })
    assert response.status_code == 422
    
    # Test valid data
    response = await client.post("/api/encoders", json={
        "name": "Test Encoder",
        "ip_address": "192.168.1.100",
        "serial_number": "ABC123456"
    })
    assert response.status_code == 201 