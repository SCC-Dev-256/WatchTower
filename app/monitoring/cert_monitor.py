from cryptography import x509
from cryptography.hazmat.backends import default_backend
import datetime
import ssl
import socket
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from flask import current_app
from cryptography.x509.oid import ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import requests
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from cryptography import ocsp
from cryptography.hazmat import serialization
import threading
import time
from app.core.error_handling import handle_errors
from app.core.aja_remediation_service import AJARemediationService
from app.core.error_handling.handlers import ErrorHandler

logger = logging.getLogger(__name__)

@dataclass
class CertificateInfo:
    """Certificate information container"""
    issuer: Dict
    subject: Dict
    expires: datetime.datetime
    days_remaining: int
    needs_renewal: bool
    serial_number: str
    version: int
    algorithm: str

class CertificateMonitor:
    def __init__(self, app=None):
        self.app = app
        self.check_interval = 86400  # 24 hours
        self.renewal_threshold = 30  # days
        self.last_check = {}
        self.chain_validator = CertificateChainValidator()
        self._monitor_thread = None
        self._should_stop = False
        self.error_handler = ErrorHandler(app)
        self.auto_remediation = AJARemediationService(app)
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['certificate_monitor'] = self
        app.before_first_request(self.start_monitoring)
        app.teardown_appcontext(self.shutdown_monitoring)
        
    def start_monitoring(self):
        """Start certificate monitoring"""
        if self._monitor_thread is None:
            self._should_stop = False
            self._monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name='cert-monitor'
            )
            self._monitor_thread.start()
            logger.info("Certificate monitoring started")
            
    def shutdown_monitoring(self, exception=None):
        """Gracefully shutdown monitoring"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.info("Shutting down certificate monitoring...")
            self._should_stop = True
            self._monitor_thread.join(timeout=30)  # Wait up to 30s
            if self._monitor_thread.is_alive():
                logger.warning("Certificate monitor thread did not stop gracefully")
            self._monitor_thread = None

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self._should_stop:
            try:
                with self.app.app_context():
                    domain = self.app.config['DOMAIN']
                    
                    # Check certificate
                    cert_info = self.check_cert_expiry(domain)
                    
                    # Verify chain
                    chain_valid = self.verify_cert_chain(domain)
                    
                    # Update metrics with enhanced data
                    if 'certificate_metrics' in self.app.extensions:
                        metrics = self.app.extensions['certificate_metrics']
                        metrics.update_metrics(domain, {
                            **cert_info.__dict__,
                            'chain_valid': chain_valid,
                            'validation_failures': self.error_handler.fallback_attempts.get(domain, []),
                            'last_check_time': datetime.utcnow(),
                            'ocsp_status': self._check_ocsp_status(cert_info),
                            'crl_status': self._check_crl_status(cert_info)
                        })
                        
                        # Cleanup stale metrics older than 30 days
                        metrics.cleanup_stale_metrics(timedelta(days=30))
                    
                    # Handle renewal if needed
                    if cert_info.needs_renewal:
                        self._handle_renewal(domain, cert_info)
                        
            except Exception as e:
                logger.error(f"Error in certificate monitoring: {str(e)}")
                
            # Sleep until next check, but allow interruption
            for _ in range(self.check_interval):
                if self._should_stop:
                    break
                time.sleep(1)
                
    def _handle_renewal(self, domain: str, cert_info: CertificateInfo):
        """Handle certificate renewal process"""
        try:
            from .cert_renewal import CertificateRenewal
            
            renewal = CertificateRenewal(
                domain=domain,
                email=self.app.config['ADMIN_EMAIL']
            )
            
            result = renewal.renew_certificate()
            
            if result['status'] == 'success':
                logger.info(f"Certificate renewed for {domain}")
                renewal.reload_webserver()
            else:
                # Handle renewal failure with recovery
                recovery_result = self.error_handler.handle_renewal_failure(
                    domain, Exception(result['message'])
                )
                if recovery_result['status'] == 'warning':
                    logger.warning(f"Certificate renewal recovered: {recovery_result['message']}")
                else:
                    logger.error(f"Certificate renewal failed: {recovery_result['message']}")
                    self._alert_on_failure(domain, f"Renewal failed: {recovery_result['message']}")
                
        except Exception as e:
            logger.error(f"Error during certificate renewal: {str(e)}")
            self._alert_on_failure(domain, f"Renewal error: {str(e)}")

    @handle_errors()
    def check_cert_expiry(self, domain: str, port: int = 443) -> CertificateInfo:
        """Check SSL certificate expiration and details"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    x509_cert = x509.load_der_x509_certificate(cert, default_backend())
                    
                    days_to_expire = (x509_cert.not_valid_after - 
                                    datetime.datetime.utcnow()).days
                    
                    cert_info = CertificateInfo(
                        issuer=dict(x509_cert.issuer),
                        subject=dict(x509_cert.subject),
                        expires=x509_cert.not_valid_after,
                        days_remaining=days_to_expire,
                        needs_renewal=days_to_expire < self.renewal_threshold,
                        serial_number=format(x509_cert.serial_number, 'x'),
                        version=x509_cert.version,
                        algorithm=x509_cert.signature_algorithm_oid._name
                    )

                    self._log_cert_status(domain, cert_info)
                    return cert_info

        except Exception as e:
            logger.error(f"Certificate check failed for {domain}: {str(e)}")
            self._alert_on_failure(domain, str(e))
            raise

    def _log_cert_status(self, domain: str, cert_info: CertificateInfo):
        """Log certificate status and trigger alerts if needed"""
        if cert_info.needs_renewal:
            logger.warning(
                f"Certificate for {domain} needs renewal. "
                f"Expires in {cert_info.days_remaining} days"
            )
            self._send_renewal_alert(domain, cert_info)
        else:
            logger.info(
                f"Certificate for {domain} valid for {cert_info.days_remaining} days"
            )

    def _send_renewal_alert(self, domain: str, cert_info: CertificateInfo):
        """Send alert for certificate renewal"""
        from ..core.security.security_logger import SecurityEventLogger
        security_logger = SecurityEventLogger(self.app)
        
        security_logger.log_ssl_event("certificate_expiring", {
            'domain': domain,
            'days_remaining': cert_info.days_remaining,
            'issuer': cert_info.issuer,
            'expires': cert_info.expires.isoformat()
        })

    def _alert_on_failure(self, domain: str, error: str):
        """Alert on certificate check failure"""
        from ..core.security.security_logger import SecurityEventLogger
        security_logger = SecurityEventLogger(self.app)
        
        security_logger.log_ssl_event("certificate_check_failed", {
            'domain': domain,
            'error': error
        })

    @handle_errors(retry_count=3, retry_delay=5)
    def verify_cert_chain(self, domain: str) -> bool:
        """Enhanced certificate chain validation with fallbacks"""
        try:
            # Standard SSL verification
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_chain = ssock.get_peer_cert_chain()
            
            # Verify each cert in chain
            for i in range(len(cert_chain) - 1):
                cert = cert_chain[i]
                issuer = cert_chain[i + 1]
                if not self._verify_cert_signature(cert, issuer):
                    if self._try_alternate_chain_paths(cert):
                        continue
                    return False
            return True
            
        except ssl.SSLError as e:
            logger.error(f"Chain validation failed: {str(e)}")
            # Try manual chain building
            return self._try_manual_chain_building(domain)

    def _validate_chain(self, cert_chain: Dict) -> bool:
        """Validate the certificate chain is properly formed and trusted"""
        try:
            if not cert_chain:
                return False
                
            # Check certificate attributes
            if 'subject' not in cert_chain or 'issuer' not in cert_chain:
                return False
                
            # Verify chain length
            if 'chain' in cert_chain:
                chain = cert_chain['chain']
                if len(chain) < 2:  # Need at least leaf and intermediate
                    logger.warning("Certificate chain too short")
                    return False
                    
            # Verify trust anchors
            context = ssl.create_default_context()
            context.load_default_certs()
            
            # Verify revocation status
            context.verify_flags = ssl.VERIFY_CRL_CHECK_CHAIN
            
            return context.verify_certificate_chain(cert_chain)
            
        except Exception as e:
            logger.error(f"Chain validation error: {str(e)}")
            return False

class CertificateChainValidator:
    """Handles certificate chain validation and OCSP checking"""
    
    def __init__(self):
        self.root_store = self._load_root_store()
        self.ocsp_cache = {}  # Cache OCSP responses
        
    def _load_root_store(self) -> List[x509.Certificate]:
        """Load trusted root CA certificates"""
        root_certs = []
        root_paths = [
            "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu
            "/etc/pki/tls/certs/ca-bundle.crt",    # RHEL/CentOS
            "/etc/ssl/ca-bundle.pem",              # SUSE
        ]
        
        for path in root_paths:
            try:
                with open(path, 'rb') as f:
                    pem_data = f.read()
                    certs = x509.load_pem_x509_certificates(pem_data)
                    root_certs.extend(certs)
                break  # Use first available CA bundle
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.error(f"Error loading root certificates: {str(e)}")
                
        if not root_certs:
            raise RuntimeError("No root certificates found")
            
        return root_certs
        
    def verify_chain(self, cert_chain: List[x509.Certificate]) -> Tuple[bool, Optional[str]]:
        """
        Verify the certificate chain including:
        - Chain integrity
        - Signature verification
        - Trust anchor validation
        - Revocation status
        """
        try:
            if not cert_chain:
                return False, "Empty certificate chain"
                
            # Verify chain length
            if len(cert_chain) < 2:
                return False, "Certificate chain too short"
                
            # Verify chain order (leaf -> intermediate -> root)
            for i in range(len(cert_chain) - 1):
                current = cert_chain[i]
                issuer = cert_chain[i + 1]
                
                # Verify certificate signatures
                if not self._verify_signature(current, issuer):
                    return False, f"Invalid signature at chain position {i}"
                    
                # Verify issuer/subject chaining
                if current.issuer != issuer.subject:
                    return False, f"Invalid issuer/subject chain at position {i}"
                    
            # Verify against root store
            root_cert = cert_chain[-1]
            if not self._verify_root(root_cert):
                return False, "Root certificate not trusted"
                
            # Check OCSP status
            leaf_cert = cert_chain[0]
            if not self._check_ocsp_status(leaf_cert, cert_chain[1]):
                return False, "Certificate revoked or OCSP check failed"
                
            return True, None
            
        except Exception as e:
            logger.error(f"Chain validation error: {str(e)}")
            return False, str(e)
            
    def _verify_signature(self, cert: x509.Certificate, issuer: x509.Certificate) -> bool:
        """Verify certificate signature"""
        try:
            public_key = issuer.public_key()
            public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm
            )
            return True
        except InvalidSignature:
            return False
            
    def _verify_root(self, cert: x509.Certificate) -> bool:
        """Verify if certificate is in trusted root store"""
        cert_fingerprint = cert.fingerprint(hashes.SHA256())
        return any(
            cert_fingerprint == root.fingerprint(hashes.SHA256())
            for root in self.root_store
        )
        
    def _check_ocsp_status(self, cert: x509.Certificate, issuer: x509.Certificate) -> bool:
        """Enhanced OCSP status check with fallbacks"""
        try:
            # Get OCSP URL
            ocsp_urls = self._get_ocsp_urls(cert)
            if not ocsp_urls:
                logger.warning("No OCSP URLs found, falling back to CRL check")
                return self._check_crl_status(cert)
                
            for ocsp_url in ocsp_urls:
                try:
                    # Try each OCSP responder with timeout
                    with requests.Session() as session:
                        response = session.post(
                            ocsp_url,
                            data=self._build_ocsp_request(cert, issuer),
                            headers={'Content-Type': 'application/ocsp-request'},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            return self._validate_ocsp_response(response.content)
                            
                except requests.Timeout:
                    logger.warning(f"OCSP responder {ocsp_url} timed out")
                    continue
                    
            # If all OCSP attempts fail, try CRL
            logger.warning("All OCSP attempts failed, falling back to CRL")
            return self._check_crl_status(cert)
            
        except Exception as e:
            logger.error(f"OCSP check failed: {str(e)}")
            # Last resort - check certificate dates only
            return datetime.utcnow() < cert.not_valid_after
        
    def _get_ocsp_urls(self, cert: x509.Certificate) -> List[str]:
        """Get OCSP URLs from certificate extensions"""
        ocsp_urls = []
        ocsp_ext = cert.extensions.get_extension_for_oid(
            ExtensionOID.AUTHORITY_INFORMATION_ACCESS
        )
        for desc in ocsp_ext.value:
            if desc.access_method.dotted_string == "1.3.6.1.5.5.7.48.1":
                ocsp_urls.append(desc.access_location.value)
        return ocsp_urls
        
    def _build_ocsp_request(self, cert: x509.Certificate, issuer: x509.Certificate) -> bytes:
        """Build OCSP request"""
        builder = ocsp.OCSPRequestBuilder()
        builder = builder.add_certificate(cert, issuer, hashes.SHA1())
        return builder.build().public_bytes(serialization.Encoding.DER)
        
    def _validate_ocsp_response(self, response: bytes) -> bool:
        """Validate OCSP response"""
        ocsp_response = ocsp.load_der_ocsp_response(response)
        return ocsp_response.certificate_status == ocsp.OCSPCertStatus.GOOD
        
    def _check_crl_status(self, cert: x509.Certificate) -> bool:
        """Check certificate revocation status via CRL"""
        context = ssl.create_default_context()
        context.load_default_certs()
        context.verify_flags = ssl.VERIFY_CRL_CHECK_CHAIN
        return context.verify_certificate_chain([cert])
        
    def _verify_root(self, cert: x509.Certificate) -> bool:
        """Verify if certificate is in trusted root store"""
        cert_fingerprint = cert.fingerprint(hashes.SHA256())
        return any(
            cert_fingerprint == root.fingerprint(hashes.SHA256())
            for root in self.root_store
        )