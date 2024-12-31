from datetime import datetime, timedelta
from typing import Dict, Optional
from app.core.error_handling.errors.exceptions import APIError
from app.core.error_handling.handlers import ErrorHandler

class CertificateErrorHandler(ErrorHandler):
    """Specialized handler for certificate-related errors"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.fallback_attempts = {}
        self.retry_config = {
            'max_attempts': 3,
            'delay_seconds': 5,
            'backoff_factor': 2.0,
            'max_delay': 300
        }

    async def handle_renewal_failure(self, domain: str, error: Exception) -> Dict:
        """Handle certificate renewal failures"""
        try:
            error_data = self._prepare_error_data(error, {'domain': domain})
            
            # Check for recent attempts
            if self._too_many_recent_attempts(domain):
                return self._handle_rate_limit(domain)

            # Try fallback methods
            for method in ['dns_challenge', 'http_challenge', 'self_signed']:
                try:
                    result = await self._try_fallback_method(method, domain)
                    if result['success']:
                        return result
                except Exception as e:
                    self.logger.warning(f"Fallback {method} failed: {str(e)}")

            # If all fallbacks fail, handle critical failure
            return self._handle_critical_failure(domain, error_data)

        except Exception as e:
            self.logger.error(f"Certificate error recovery failed: {str(e)}")
            raise APIError(
                message="Certificate recovery failed",
                code=500,
                details={'domain': domain, 'error': str(e)}
            ) 