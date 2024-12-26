from typing import Optional
import logging
from .cert_monitor import CertificateMonitor, CertificateInfo
from .cert_renewal import CertificateRenewal
from .cert_metrics import CertificateMetrics

logger = logging.getLogger(__name__)

class CertificateManager:
    """Manages certificate monitoring and renewal"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        self.app = app
        self.domain = app.config['DOMAIN']
        self.email = app.config['ADMIN_EMAIL']
        
        self.monitor = CertificateMonitor(app)
        self.renewal = CertificateRenewal(self.domain, self.email)
        self.metrics = CertificateMetrics()
        
    def check_and_renew(self) -> Optional[dict]:
        """Check certificate status and renew if needed"""
        try:
            cert_info = self.monitor.check_cert_expiry(self.domain)
            self.metrics.update_metrics(self.domain, cert_info)
            
            if cert_info.needs_renewal:
                result = self.renewal.renew_certificate()
                self.metrics.record_renewal_attempt(
                    self.domain,
                    result['status']
                )
                
                if result['status'] == 'success':
                    self.renewal.reload_webserver()
                    
                return result
                
            return None
            
        except Exception as e:
            logger.error(f"Certificate management failed: {str(e)}")
            self.metrics.record_check_error(self.domain, str(e))
            return {'status': 'error', 'message': str(e)} 