import pytest
from app.services.stream_validator import StreamConfigValidator, StreamingConfig

@pytest.fixture
def stream_validator():
    return StreamConfigValidator()

@pytest.fixture
def valid_config():
    return StreamingConfig(
        resolution="1920x1080",
        fps=30,
        bitrate=5_000_000,
        rtmp_key="valid_rtmp_key"
    )

@pytest.fixture
def invalid_config():
    return StreamingConfig(
        resolution="4000x2000",
        fps=120,
        bitrate=50_000_000,
        rtmp_key="short"
    )

def test_validate_config_success(stream_validator, valid_config):
    result = stream_validator.validate_config(valid_config)
    assert result.valid is True
    assert not result.issues
    assert not result.warnings

def test_validate_config_failure(stream_validator, invalid_config):
    result = stream_validator.validate_config(invalid_config)
    assert result.valid is False
    assert len(result.issues) > 0

# Additional tests for other methods and scenarios can be added here 