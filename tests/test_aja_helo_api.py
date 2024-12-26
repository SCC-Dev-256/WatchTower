import pytest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectionError, HTTPError
from app.services.aja_helo_api import AJAHeloAPI
from app.core.error_handler import EncoderConnectionError, EncoderAuthenticationError

@pytest.fixture
def helo_api():
    return AJAHeloAPI('192.168.1.100')

@pytest.fixture
def mock_response():
    response = Mock()
    response.json.return_value = {'status': 'success'}
    return response

def test_streaming_status(helo_api, mock_response):
    with patch('requests.Session.request', return_value=mock_response):
        result = helo_api.get_streaming_status()
        assert result == {'status': 'success'}

def test_connection_error(helo_api):
    with patch('requests.Session.request', side_effect=ConnectionError()):
        with pytest.raises(EncoderConnectionError):
            helo_api.get_streaming_status()

def test_authentication_error(helo_api):
    response = Mock()
    response.status_code = 401
    with patch('requests.Session.request', side_effect=HTTPError(response=response)):
        with pytest.raises(EncoderAuthenticationError):
            helo_api.get_streaming_status() 