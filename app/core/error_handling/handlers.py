from datetime import datetime
from typing import Dict, Optional
import logging
from flask import current_app
from app.core.error_handling.errors.exceptions import APIError, EncoderError, AJAStreamError
from .responses import APIResponse
from app.monitoring.error_analysis import ErrorAnalyzer
from app.core.aja.aja_remediation_service import AJARemediationService
from app.core.aja.client import AJAHELOClient
from app.core.error_handling.decorators import handle_errors
from app.core.error_handling.ErrorLogging import ErrorLogger

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

class StreamErrorHandler(ErrorHandler):
    """Specialized handler for streaming-related errors"""
    
    def __init__(self, app=None):
        super().__init__(app)
        self.stream_thresholds = app.config.get('STREAM_THRESHOLDS', {})
        self.aja_client = AJAHELOClient(app.config['AJA_IP'])

    @handle_errors
    async def handle_stream_error(self, encoder_id: str, stream_data: Dict, error: Exception) -> Dict:
        """Handle streaming-related errors"""
        # Log the error
        self.log_error({
            'encoder_id': encoder_id,
            'error': str(error),
            'stream_data': stream_data
        }, error_type='stream', severity='critical')
        
        error_data = self._prepare_error_data(error, {
            'encoder_id': encoder_id,
            'stream_data': stream_data
        })

        # Analyze stream health
        health_check = await self._check_stream_health(encoder_id)
        if health_check['critical']:
            return await self._handle_critical_stream_failure(error_data)

        # Handle normal stream issues
        return await self._handle_stream_issue(error_data)

    async def _check_stream_health(self, encoder_id: str) -> Dict:
        """Check stream health metrics"""
        metrics = await self.app.encoder_service.get_metrics(encoder_id)
        
        return {
            'critical': any(
                metrics[key] > self.stream_thresholds[key]
                for key in ['packet_loss', 'latency', 'jitter']
                if key in metrics and key in self.stream_thresholds
            ),
            'metrics': metrics
        }

    async def _handle_critical_stream_failure(self, error_data: Dict) -> Dict:
        """Handle critical stream failures"""
        # Implement logic for handling critical failures
        pass

    async def _handle_stream_issue(self, error_data: Dict) -> Dict:
        """Handle non-critical stream issues"""
        # Implement logic for handling non-critical issues
        pass

    def _prepare_error_data(self, error: Exception, context: Dict) -> Dict:
        """Prepare error data for logging and handling"""
        return {
            'error_message': str(error),
            'context': context
        }

    def log_error(self, error_data: Dict, error_type: str, severity: str):
        """Log error details"""
        self.logger.log_error(error_data, error_type=error_type, severity=severity) 