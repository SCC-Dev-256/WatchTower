from typing import Dict
from datetime import datetime
from app.core.error_handling.central_error_manager import ErrorHandler


class PerformanceMonitor:
    def __init__(self, app):
        self.metrics = {}
        self.thresholds = {
            'latency': 200,      # ms
            'message_rate': 100,  # messages per second
            'processing_time': 50 # ms
        }
        self.error_handler = ErrorHandler(app)

    async def record_client_metrics(self, client_id: str, metrics: Dict):
        """Record performance metrics for a client"""
        try:
            self.metrics[client_id] = {
                'timestamp': datetime.utcnow(),
                'data': metrics
            }
        except Exception as e:
            await self.error_handler.handle_performance_error(client_id, e)

    async def get_performance_metrics(self) -> Dict:
        """Get aggregated performance metrics"""
        return {
            'clients': len(self.metrics),
            'average_latency': self._calculate_average_latency(),
            'message_rate': self._calculate_message_rate(),
            'issues': self._detect_performance_issues()
        } 