from datetime import datetime
from typing import Dict, Optional
import logging
from flask import current_app
from app.core.error_handling.errors.exceptions import APIError, EncoderError, AJAStreamError
from .responses import APIResponse
from app.core.error_handling.analysis.correlation_analyzer import ErrorAnalyzer
from app.core.aja.aja_remediation_service import AJARemediationService
from app.core.aja.client import AJAHELOClient
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.error_logging import ErrorLogger

class ErrorHandler:
    def __init__(self, app=None):
        self.app = app
        self.logger = ErrorLogger(app)
        self.error_analyzer = ErrorAnalyzer(app) if app else None
        self.auto_remediation = AJARemediationService(app) if app else None

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> tuple:
        """Central error handling method"""
        error_data = self._prepare_error_data(error, context)
        
        # Log the error
        self._log_error(error_data)
        
        # Analyze error if it's encoder-related
        if isinstance(error, EncoderError):
            analysis = self._analyze_error(error_data)
            error_data['analysis'] = analysis
            
            # Attempt auto-remediation if enabled
            if self.app.config.get('AUTO_REMEDIATION_ENABLED'):
                remediation = self._attempt_remediation(error_data)
                error_data['remediation'] = remediation

        # Prepare API response
        response = APIResponse(
            error=error,
            error_data=error_data,
            analysis=error_data.get('analysis'),
            remediation=error_data.get('remediation')
        )

        return response

    def handle_certificate_error(self, error: Exception, context: Dict) -> Dict:
        """Handle certificate errors"""
        error_data = self._prepare_error_data(error, context)
        self.logger.error(f"Certificate error: {error_data}")
        return {'status': 'error', 'details': error_data}

    def _prepare_error_data(self, error: Exception, context: Optional[Dict]) -> Dict:
        """Prepare error data for logging and analysis"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'details': getattr(error, 'details', {}),
            'code': getattr(error, 'code', 500)
        }

    def _log_error(self, error_data: Dict):
        """Log error with appropriate severity"""
        if error_data['code'] >= 500:
            self.logger.error(error_data)
        else:
            self.logger.warning(error_data)

    def _analyze_error(self, error_data: Dict) -> Dict:
        """Analyze error using ErrorAnalyzer"""
        if self.error_analyzer:
            return self.error_analyzer.analyze_error(error_data)
        return {}

    def _attempt_remediation(self, error_data: Dict) -> Dict:
        """Attempt auto-remediation"""
        if self.auto_remediation:
            return self.auto_remediation.attempt_remediation(error_data)
        return {}
