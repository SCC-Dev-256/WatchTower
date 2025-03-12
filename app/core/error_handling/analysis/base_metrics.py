from typing import Dict, Any, Optional
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram
from app.core.error_handling import ErrorType

# This file contains the BaseMetricsService class, which is used to collect and track metrics for encoders.
# The BaseMetricsService class has the following methods:
# - increment_operation: Increments the operation counter.
# - record_error: Records an error.
# - update_health: Updates the health score.
# - record_duration: Records the duration of an operation.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `increment_operation`, `record_error`, `update_health`, and `record_duration` methods.
# - Detailed implementation for methods like `log_and_track`.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `increment_operation`, `record_error`, `update_health`, and `record_duration` methods.


class BaseMetricsService:
    """Base class for standardized metrics collection"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Initialize standard metrics
        self.operation_counter = Counter(
            f'{service_name}_operations_total',
            'Number of operations performed',
            ['operation', 'status']
        )
        
        self.error_counter = Counter(
            f'{service_name}_errors_total',
            'Number of errors encountered',
            ['error_type']
        )
        
        self.health_gauge = Gauge(
            f'{service_name}_health_score',
            'Current health score',
            ['component']
        )
        
        self.latency_histogram = Histogram(
            f'{service_name}_operation_duration_seconds',
            'Operation duration in seconds',
            ['operation']
        )

    async def increment_operation(self, operation: str, status: str = 'success'):
        """Track operation execution"""
        self.operation_counter.labels(operation=operation, status=status).inc()

    async def record_error(self, error_type: ErrorType):
        """Track error occurrence"""
        self.error_counter.labels(error_type=error_type.value).inc()

    async def update_health(self, component: str, score: float):
        """Update health score"""
        self.health_gauge.labels(component=component).set(score)

    async def record_duration(self, operation: str, duration: float):
        """Record operation duration"""
        self.latency_histogram.labels(operation=operation).observe(duration)

    async def log_and_track(self, 
                           message: str,
                           operation: str,
                           level: str = 'info',
                           error_type: Optional[ErrorType] = None,
                           metrics: Optional[Dict[str, Any]] = None,
                           **kwargs):
        """Combined logging and metrics tracking"""
        # Log the event
        log_data = {
            'service': self.service_name,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if metrics:
            log_data['metrics'] = metrics
            
        getattr(self.logger, level)(message, extra=log_data)
        
        # Track in metrics
        if error_type:
            await self.record_error(error_type)
            await self.increment_operation(operation, 'failure')
        else:
            await self.increment_operation(operation, 'success')
            
        # Record metrics if provided
        if metrics and isinstance(metrics, dict):
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    await self.update_health(f"{operation}_{key}", value) 