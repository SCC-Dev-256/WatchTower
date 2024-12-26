from typing import Dict, Optional, List
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram
from app.monitoring.error_analysis import ErrorAnalyzer
from app.monitoring.error_tracking import ErrorTracker
from app.core.error_handling.monitoring_handler import MonitoringErrorHandler
from app.core.error_handling.error_types import ErrorType

class CentralErrorManager:
    """Central Error Management System"""
    
    def __init__(self, app):
        self.app = app
        self.error_analyzer = ErrorAnalyzer(app)
        self.error_tracker = ErrorTracker(app)
        self.monitoring_handler = MonitoringErrorHandler(app)
        self.logger = logging.getLogger(__name__)
        
        # Unified metrics
        self.metrics = {
            'total_errors': Counter('total_errors', 'Total errors by type', ['error_type', 'source']),
            'error_duration': Histogram('error_duration', 'Error duration until resolution'),
            'active_errors': Gauge('active_errors', 'Currently active errors', ['severity'])
        }

    async def process_error(self, 
                          error: Exception, 
                          source: str,
                          context: Dict,
                          error_type: Optional[ErrorType] = None) -> Dict:
        """Process and track error through all systems"""
        
        # Create unified error entry
        error_entry = {
            'timestamp': datetime.utcnow(),
            'error_type': error_type or self._determine_error_type(error),
            'source': source,
            'message': str(error),
            'context': context
        }

        # Track in central system
        self.error_tracker.track_error(error, context)
        
        # Analyze error patterns
        analysis = await self.error_analyzer.analyze_error(error_entry)
        
        # Update metrics
        self._update_metrics(error_entry, analysis)
        
        # Handle specific error types
        if source == 'helo':
            await self._handle_helo_error(error_entry, analysis)
        elif source == 'monitoring':
            await self.monitoring_handler.handle_metric_error(
                context.get('encoder_id'),
                context.get('metric_type'),
                error
            )

        return {
            'error_entry': error_entry,
            'analysis': analysis,
            'handled': True
        }

    async def _handle_helo_error(self, error_entry: Dict, analysis: Dict):
        """Reference to HeloPoolErrorHandler"""
        # Reference to existing HeloPoolErrorHandler
        # Lines 27-134 in helo_pool_error_handler.py
        pass

    def _update_metrics(self, error_entry: Dict, analysis: Dict):
        """Update unified metrics"""
        self.metrics['total_errors'].labels(
            error_entry['error_type'],
            error_entry['source']
        ).inc()
        
        if analysis['severity'] in ['critical', 'high']:
            self.metrics['active_errors'].labels(analysis['severity']).inc() 