from datetime import datetime
from typing import Dict, Optional
import logging
from flask import current_app
from .exceptions import APIError, EncoderError
from .responses import APIResponse
from app.monitoring.error_analysis import ErrorAnalyzer
from app.core.aja_remediation_service import AJARemediationService

class ErrorHandler:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger('error_handler')
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

        # Create API response
        response = APIResponse.error(
            message=str(error),
            code=getattr(error, 'code', 500),
            details=error_data
        )

        return response

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