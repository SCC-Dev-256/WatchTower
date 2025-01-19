import pytest
from app.installer.bootstrap import Bootstrapper
from unittest.mock import patch, MagicMock

@pytest.fixture
def bootstrapper():
    return Bootstrapper()

@patch('app.installer.bootstrap.requests.get')
def test_fetch_config_success(mock_get, bootstrapper):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.text = '{"requirements": [], "directories": []}'
    mock_get.return_value = mock_response

    assert bootstrapper.fetch_config() is True

@patch('app.installer.bootstrap.requests.get')
def test_fetch_config_failure(mock_get, bootstrapper):
    mock_get.side_effect = Exception("Failed to fetch")

    assert bootstrapper.fetch_config() is True  # Should fall back to local config

@patch('app.installer.bootstrap.create_engine')
def test_validate_database_connection_success(mock_create_engine, bootstrapper):
    mock_engine = MagicMock()
    mock_connection = MagicMock()
    mock_engine.connect.return_value = mock_connection
    mock_create_engine.return_value = mock_engine

    assert bootstrapper.validate_database_connection() is True

@patch('app.installer.bootstrap.create_engine')
def test_validate_database_connection_failure(mock_create_engine, bootstrapper):
    mock_create_engine.side_effect = Exception("Connection failed")

    assert bootstrapper.validate_database_connection() is False

# Additional tests for other methods can be added here 