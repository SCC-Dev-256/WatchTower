from typing import Dict
from datetime import datetime
from app.core.error_handling import HandleErrors


class PerformanceMonitor:
    """Monitors and logs performance metrics."""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = {}

    def record_client_metrics(self, encoder_id: str, metrics: Dict):
        """Record performance metrics for a given encoder.
        
        Args:
            encoder_id: ID of the encoder being monitored
            metrics: Dict containing performance metrics like:
                - response_time: API response latency in ms
                - cpu_usage: CPU utilization percentage 
                - memory_usage: Memory utilization in MB
                - throughput: Messages processed per second
                - error_rate: Percentage of failed operations
        """
        timestamp = datetime.utcnow()
        
        if encoder_id not in self.metrics:
            self.metrics[encoder_id] = {
                'history': [],
                'averages': {
                    'response_time': 0,
                    'cpu_usage': 0,
                    'memory_usage': 0,
                    'throughput': 0,
                    'error_rate': 0
                }
            }
            
        # Add timestamp to metrics
        metrics['timestamp'] = timestamp
        
        # Store historical data
        self.metrics[encoder_id]['history'].append(metrics)
        
        # Update running averages
        for metric_name in ['response_time', 'cpu_usage', 'memory_usage', 'throughput', 'error_rate']:
            if metric_name in metrics:
                current_avg = self.metrics[encoder_id]['averages'][metric_name]
                new_value = metrics[metric_name]
                self.metrics[encoder_id]['averages'][metric_name] = (current_avg + new_value) / 2
                
        # Log if any metrics exceed thresholds
        self._check_thresholds(encoder_id, metrics)