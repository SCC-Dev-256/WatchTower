from datetime import datetime
from typing import Dict, Optional
import logging
from flask import current_app
from app.core.error_handling.errors.exceptions import APIError, EncoderError, AJAStreamError
from .responses import APIResponse
from app.core.error_handling import ErrorAnalyzer #not functional yet
from app.core.aja.aja_remediation_service import AJARemediationService
from app.core.aja.client import AJAHELOClient
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.error_logging import ErrorLogger
from app.core.error_handling.central_error_manager import CentralErrorManager

class ErrorHandler:
    def __init__(self, app=None):
        self.app = app
        self.logger = ErrorLogger(app)
        self.error_analyzer = ErrorAnalyzer(app) if app else None
        self.auto_remediation = AJARemediationService(app) if app else None
        self.central_manager = CentralErrorManager(app)

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> tuple:
        """Central error handling method using CentralErrorManager"""
        error_data = self.prepare_error_data(error, context)
        
        # Delegate error handling to CentralErrorManager
        error_response = self.central_manager.process_error(
            error, 
            source='error_handler', 
            context=context or {},
            error_type=type(error).__name__
        )

        # Prepare API response
        response = APIResponse(
            error=error,
            error_data=error_response['error_entry'],
            analysis=error_response.get('analysis'),
            remediation=error_response.get('remediation')
        )

        return response

    def handle_certificate_error(self, error: Exception, context: Dict) -> Dict:
        """Handle certificate errors"""
        error_data = self.prepare_error_data(error, context)
        self.logger.error(f"Certificate error: {error_data}")
        return {'status': 'error', 'details': error_data}

    def prepare_error_data(self, error: Exception, context: Optional[Dict]) -> Dict:
        """Prepare error data for logging and analysis"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'details': getattr(error, 'details', {}),
            'code': getattr(error, 'code', 500)
        }

    def log_error(self, error_data: Dict):
        """Log error with appropriate severity"""
        if error_data['code'] >= 500:
            self.logger.error(error_data)
        else:
            self.logger.warning(error_data)

    def analyze_error(self, error_data: Dict) -> Dict:
        """Analyze error using ErrorAnalyzer"""
        if self.error_analyzer:
            return self.error_analyzer.analyze_error(error_data)
        return {}

    def attempt_remediation(self, error_data: Dict) -> Dict:
        """Attempt auto-remediation"""
        if self.auto_remediation:
            return self.auto_remediation.attempt_remediation(error_data)
        return {}
