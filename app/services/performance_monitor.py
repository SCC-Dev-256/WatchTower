from typing import Dict
from datetime import datetime
from app.core.error_handling.decorators import handle_errors


class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            'latency': 200,      # ms
            'message_rate': 100,  # messages per second
            'processing_time': 50 # ms
        }

    @handle_errors()
    def record_client_metrics(self, client_id: str, metrics: Dict):
        """Record performance metrics for a client"""
        self.metrics[client_id] = {
            'timestamp': datetime.utcnow(),
            'data': metrics
        }

    @handle_errors()
    def get_performance_metrics(self) -> Dict:
        """Get aggregated performance metrics"""
        return {
            'clients': len(self.metrics),
            'average_latency': self._calculate_average_latency(),
            'message_rate': self._calculate_message_rate(),
            'issues': self._detect_performance_issues()
        } 