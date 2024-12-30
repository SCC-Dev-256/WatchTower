from prometheus_client import Counter, Histogram
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EnhancedErrorMetrics:
    """Enhanced metrics for error tracking and analysis"""
    error_counter = Counter('enhanced_error_total', 'Total enhanced errors by type and service', ['error_type', 'service'])
    error_resolution_time = Histogram('enhanced_error_resolution_seconds', 'Time to resolve enhanced errors', ['resolution_strategy'])
    error_pattern_changes = Counter('error_pattern_changes_total', 'Significant changes in error patterns', ['error_type'])

    def log_error(self, error_type: str, service: str, resolution_strategy: str, resolution_time: float) -> None:
        """Log error with detailed context and update metrics"""
        logger.error(
            f"Error occurred in service {service}",
            extra={
                'error_type': error_type,
                'service': service,
                'resolution_strategy': resolution_strategy,
                'resolution_time': resolution_time
            }
        )
        
        # Update metrics
        self.error_counter.labels(error_type=error_type, service=service).inc()
        self.error_resolution_time.labels(resolution_strategy=resolution_strategy).observe(resolution_time)

    def log_pattern_change(self, error_type: str, details: Dict[str, Any]) -> None:
        """Log significant changes in error patterns"""
        logger.info(
            f"Significant change in error pattern for {error_type}",
            extra={
                'error_type': error_type,
                'details': details
            }
        )
        
        # Update pattern change metric
        self.error_pattern_changes.labels(error_type=error_type).inc()