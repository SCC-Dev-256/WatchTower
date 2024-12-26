import pytest
from datetime import datetime, timedelta
import ssl
from unittest.mock import Mock, patch, MagicMock
from app.monitoring.cert_monitor import CertificateMonitor, CertificateInfo
from app.core.error_handling.recovery import CertificateErrorRecovery

@pytest.fixture
def app():
    """Mock Flask app fixture"""
    app = Mock()
    app.config = {
        'DOMAIN': 'example.com',
        'ADMIN_EMAIL': 'admin@example.com',
        'SSL_CERT_PATH': '/etc/ssl/certs/example.com.pem'
    }
    app.extensions = {}
    return app

@pytest.fixture
def cert_monitor(app):
    """CertificateMonitor instance with mocked dependencies"""
    monitor = CertificateMonitor(app)
    monitor.error_recovery = Mock(spec=CertificateErrorRecovery)
    return monitor

class TestCertificateMonitor:
    def test_check_cert_expiry_valid(self, cert_monitor):
        """Test certificate expiry check with valid cert"""
        with patch('ssl.create_default_context') as mock_ssl:
            # Mock SSL context and socket
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context
            mock_sock = MagicMock()
            mock_context.wrap_socket.return_value.__enter__.return_value = mock_sock
            
            # Mock certificate data
            mock_sock.getpeercert.return_value = {
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt Authority X3'),),),
                'notAfter': 'Dec 31 23:59:59 2024 GMT',
                'serialNumber': '123456789'
            }
            
            cert_info = cert_monitor.check_cert_expiry('example.com')
            assert isinstance(cert_info, CertificateInfo)
            assert cert_info.days_remaining > 0
            assert not cert_info.needs_renewal

    def test_check_cert_expiry_near_expiration(self, cert_monitor):
        """Test certificate near expiration"""
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context
            mock_sock = MagicMock()
            
            # Set expiry date to 15 days from now
            expiry_date = (datetime.utcnow() + timedelta(days=15)).strftime('%b %d %H:%M:%S %Y GMT')
            mock_sock.getpeercert.return_value = {
                'notAfter': expiry_date,
                'subject': ((('commonName', 'example.com'),),),
                'issuer': ((('commonName', 'Let\'s Encrypt Authority X3'),),),
                'serialNumber': '123456789'
            }
            mock_context.wrap_socket.return_value.__enter__.return_value = mock_sock
            
            cert_info = cert_monitor.check_cert_expiry('example.com')
            assert cert_info.needs_renewal
            assert 14 <= cert_info.days_remaining <= 16

    @pytest.mark.parametrize("error,expected_retries", [
        (ssl.SSLError("Certificate validation failed"), 3),
        (ConnectionError("Connection refused"), 3),
        (TimeoutError("Connection timeout"), 3)
    ])
    def test_cert_check_with_errors(self, cert_monitor, error, expected_retries):
        """Test error handling and retry logic"""
        with patch('ssl.create_default_context') as mock_ssl:
            mock_ssl.side_effect = error
            
            # Configure error recovery mock
            cert_monitor.error_recovery.with_retry.return_value = Mock(side_effect=error)
            
            with pytest.raises(type(error)):
                cert_monitor.check_cert_expiry('example.com')
            
            # Verify retry attempts
            assert cert_monitor.error_recovery.fallback_attempts.get('certificate_check', [])

    def test_verify_cert_chain_valid(self, cert_monitor):
        """Test successful certificate chain validation"""
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context
            
            # Mock certificate chain
            mock_chain = [Mock() for _ in range(3)]  # Leaf, intermediate, root
            mock_sock = MagicMock()
            mock_sock.get_peer_cert_chain.return_value = mock_chain
            mock_context.wrap_socket.return_value.__enter__.return_value = mock_sock
            
            # Mock signature verification
            cert_monitor._verify_cert_signature = Mock(return_value=True)
            
            assert cert_monitor.verify_cert_chain('example.com')

    def test_verify_cert_chain_invalid(self, cert_monitor):
        """Test invalid certificate chain detection"""
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = MagicMock()
            mock_ssl.return_value = mock_context
            
            # Mock invalid chain
            mock_chain = [Mock()]  # Too short
            mock_sock = MagicMock()
            mock_sock.get_peer_cert_chain.return_value = mock_chain
            mock_context.wrap_socket.return_value.__enter__.return_value = mock_sock
            
            assert not cert_monitor.verify_cert_chain('example.com')

    def test_monitoring_loop_lifecycle(self, cert_monitor):
        """Test monitoring loop lifecycle and cleanup"""
        with patch.object(cert_monitor, 'check_cert_expiry') as mock_check:
            mock_check.return_value = Mock(needs_renewal=False)
            
            # Start monitoring
            cert_monitor.start_monitoring()
            assert cert_monitor._monitor_thread.is_alive()
            
            # Shutdown monitoring
            cert_monitor.shutdown_monitoring()
            assert not cert_monitor._monitor_thread.is_alive()

    @pytest.mark.asyncio
    async def test_metrics_collection(self, cert_monitor, app):
        """Test metrics collection and cleanup"""
        mock_metrics = Mock()
        app.extensions['certificate_metrics'] = mock_metrics
        
        with patch.object(cert_monitor, 'check_cert_expiry') as mock_check:
            # Simulate successful check
            mock_check.return_value = Mock(
                needs_renewal=False,
                days_remaining=90,
                __dict__={'some_metric': 'value'}
            )
            
            # Run monitoring cycle
            cert_monitor._monitoring_loop()
            
            # Verify metrics were updated
            mock_metrics.update_metrics.assert_called_once()
            mock_metrics.cleanup_stale_metrics.assert_called_once()

    def test_certbot_integration(self, cert_monitor):
        """Test Certbot interaction during renewal"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            # Simulate renewal needed
            cert_info = Mock(needs_renewal=True)
            cert_monitor._handle_renewal('example.com', cert_info)
            
            # Verify Certbot was called
            mock_run.assert_called() 