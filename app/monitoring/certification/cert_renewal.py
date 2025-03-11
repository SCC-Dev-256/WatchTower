from datetime import datetime
import subprocess
import logging
import time
from typing import Dict, Tuple
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.auth import require_api_key, roles_required
from app.core.error_handling import handle_errors

logger = logging.getLogger(__name__)

class CertificateRenewal:
    """Handles automated certificate renewal via Certbot"""
    
    def __init__(self, domain: str, email: str, max_reload_attempts: int = 3):
        self.domain = domain
        self.email = email
        self.max_reload_attempts = max_reload_attempts
    
    @handle_errors()
    @roles_required('admin')
    @require_api_key
    def renew_certificate(self) -> Dict[str, str]:
        """Attempt to renew certificate using Certbot"""
        try:
            result = subprocess.run([
                'certbot', 'renew',
                '--noninteractive',
                '--agree-tos',
                '--email', self.email,
                '--domains', self.domain
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Certificate renewed for {self.domain}")
                return {'status': 'success', 'message': 'Certificate renewed'}
            else:
                logger.error(f"Certificate renewal failed: {result.stderr}")
                return {'status': 'error', 'message': result.stderr}
                
        except Exception as e:
            logger.error(f"Renewal process failed: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    @handle_errors()
    @roles_required('admin')
    @require_api_key
    def reload_webserver(self) -> Dict[str, str]:
        """Reload nginx after certificate renewal with retry logic and health checks"""
        try:
            # First attempt to reload
            success, message = self._attempt_reload()
            if success:
                return {'status': 'success', 'message': message}

            # If initial reload fails, attempt recovery
            recovery_success = self._handle_failed_reload()
            if recovery_success:
                return {'status': 'success', 'message': 'Recovered after initial reload failure'}
            
            return {'status': 'error', 'message': 'Failed to reload webserver after multiple attempts'}

        except Exception as e:
            logger.error(f"Critical error during webserver reload: {str(e)}")
            return {'status': 'error', 'message': f"Critical error: {str(e)}"}

    def _attempt_reload(self) -> Tuple[bool, str]:
        """Attempt to reload nginx and verify its status"""
        try:
            # Check nginx config before reload
            subprocess.run(['nginx', '-t'], check=True, capture_output=True)
            
            # Attempt reload
            subprocess.run(['systemctl', 'reload', 'nginx'], check=True)
            
            # Verify service is running
            if self._verify_webserver_health():
                return True, "Webserver reloaded successfully"
            return False, "Reload completed but health check failed"

        except subprocess.CalledProcessError as e:
            logger.error(f"Reload attempt failed: {str(e)}")
            return False, f"Reload failed: {str(e)}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _verify_webserver_health(self) -> bool:
        """Verify nginx is healthy after reload"""
        try:
            # Check systemd service status
            service_check = subprocess.run(
                ['systemctl', 'is-active', 'nginx'],
                capture_output=True,
                text=True
            )
            if service_check.stdout.strip() != 'active':
                raise Exception("Nginx service not active")

            # Attempt HTTPS connection to verify SSL
            response = requests.get(
                f"https://{self.domain}",
                timeout=5,
                verify=True
            )
            return response.status_code < 500

        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            raise

    def _handle_failed_reload(self) -> bool:
        """Recovery procedure for failed reload attempts"""
        try:
            logger.info("Attempting recovery procedure...")
            
            # Stop nginx
            subprocess.run(['systemctl', 'stop', 'nginx'], check=True)
            time.sleep(2)
            
            # Start nginx
            subprocess.run(['systemctl', 'start', 'nginx'], check=True)
            time.sleep(2)
            
            # Verify health after restart
            return self._verify_webserver_health()

        except Exception as e:
            logger.error(f"Recovery procedure failed: {str(e)}")
            return False 