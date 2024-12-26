import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.monitoring.cert_manager import CertificateManager
from app.monitoring.cert_monitor import CertificateInfo

@pytest.fixture
def app():
    # Mock Flask app
    app = Mock()
    app.config = {
        'DOMAIN': 'example.com',
        'ADMIN_EMAIL': 'admin@example.com'
    }
    return app

@pytest.fixture
def cert_manager(app):
    return CertificateManager(app)

def test_certificate_check_and_renewal(cert_manager):
    # Mock certificate info
    mock_cert_info = CertificateInfo(
        issuer={'CN': 'Test CA'},
        subject={'CN': 'example.com'},
        expires=datetime.utcnow() + timedelta(days=20),
        days_remaining=20,
        needs_renewal=True,
        serial_number='123456',
        version=3,
        algorithm='sha256WithRSAEncryption'
    )
    
    with patch('app.monitoring.cert_monitor.CertificateMonitor.check_cert_expiry') as mock_check:
        mock_check.return_value = mock_cert_info
        
        with patch('app.monitoring.cert_renewal.CertificateRenewal.renew_certificate') as mock_renew:
            mock_renew.return_value = {'status': 'success', 'message': 'Certificate renewed'}
            
            result = cert_manager.check_and_renew()
            
            assert result['status'] == 'success'
            mock_check.assert_called_once()
            mock_renew.assert_called_once() 