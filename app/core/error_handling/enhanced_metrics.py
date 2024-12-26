from prometheus_client import Counter, Gauge, Histogram, Summary
from typing import Dict, Optional
from datetime import datetime

class EnhancedErrorMetrics:
    """Enhanced error metrics tracking"""
    
    def __init__(self):
        # Error counts and types
        self.error_count = Counter(
            'error_total',
            'Total error count',
            ['error_type', 'severity', 'source']
        )
        
        # Error durations
        self.error_duration = Histogram(
            'error_duration_seconds',
            'Error duration until resolution',
            ['error_type', 'resolution_type']
        )
        
        # Recovery metrics
        self.recovery_attempts = Counter(
            'recovery_attempts_total',
            'Number of recovery attempts',
            ['error_type', 'strategy', 'success']
        )
        
        # Resource impact
        self.resource_impact = Gauge(
            'error_resource_impact',
            'Resource impact of errors',
            ['resource_type', 'error_type']
        )
        
        # Error patterns
        self.error_pattern_matches = Counter(
            'error_pattern_matches',
            'Number of matched error patterns',
            ['pattern_name', 'severity']
        )
        
        # Performance impact
        self.performance_impact = Summary(
            'error_performance_impact',
            'Performance impact of errors',
            ['subsystem', 'error_type']
        )

    def record_error(self, error: Dict):
        """Record comprehensive error metrics"""
        self.error_count.labels(
            error['error_type'],
            error['severity'],
            error['source']
        ).inc()
        
        if 'duration' in error:
            self.error_duration.labels(
                error['error_type'],
                error.get('resolution_type', 'unknown')
            ).observe(error['duration'])
            
        if 'resource_impact' in error:
            for resource, impact in error['resource_impact'].items():
                self.resource_impact.labels(
                    resource,
                    error['error_type']
                ).set(impact) 