import pytest
from unittest.mock import Mock, patch
from app.core.error_handling.errors.exceptions import AJAConnectionError, AJAAuthenticationError

#Uncertain of what this needs to be. 
#@pytest.fixture
#def helo_api():
#    return AJAHeloAPI('192.168.1.100')

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
        with pytest.raises(AJAConnectionError):
            helo_api.get_streaming_status()

def test_authentication_error(helo_api):
    response = Mock()
    response.status_code = 401
    with patch('requests.Session.request', side_effect=AJAAuthenticationError(response=response)):
        with pytest.raises(AJAAuthenticationError):
            helo_api.get_streaming_status() 