from prometheus_client import Gauge, Counter
import time
from .cert_monitor import CertificateInfo
from app.core.auth import require_api_key, roles_required
from app.core.error_handling import handle_errors


class CertificateMetrics:
    """Prometheus metrics for certificate monitoring"""
    
    def __init__(self):
        self.cert_expiry_days = Gauge(
            'ssl_certificate_expiry_days',
            'Days until certificate expires',
            ['domain']
        )
        
        self.cert_check_errors = Counter(
            'ssl_certificate_check_errors_total',
            'Total number of certificate check errors',
            ['domain', 'error_type']
        )
        
        self.renewal_attempts = Counter(
            'ssl_certificate_renewal_attempts_total',
            'Total number of certificate renewal attempts',
            ['domain', 'status']
        ) 

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def update_metrics(self, domain: str, cert_info: 'CertificateInfo'):
        """Update Prometheus metrics with certificate information"""
        self.cert_expiry_days.labels(domain=domain).set(cert_info.days_remaining)

    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def record_check_error(self, domain: str, error_type: str):
        """Record certificate check errors"""
        self.cert_check_errors.labels(
            domain=domain,
            error_type=error_type
        ).inc()
        
    @handle_errors()
    @roles_required('admin', 'editor')
    @require_api_key
    def record_renewal_attempt(self, domain: str, status: str):
        """Record certificate renewal attempts"""
        self.renewal_attempts.labels(
            domain=domain,
            status=status
        ).inc()
        
    @handle_errors()
    @roles_required('admin', 'editor', 'viewer')
    @require_api_key
    def get_metrics_summary(self) -> dict:
        """Get summary of all certificate metrics"""
        return {
            'expiry_days': self.cert_expiry_days._value.items(),
            'check_errors': self.cert_check_errors._value.items(),
            'renewal_attempts': self.renewal_attempts._value.items()
        } 