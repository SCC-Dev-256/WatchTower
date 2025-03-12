from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
from app.core import EncoderMetrics
from app.core.error_handling import handle_errors


# This file contains the MetricsAnalyzer class, which is used to analyze metrics from encoders.
# The MetricsAnalyzer class has the following methods:
# - analyze_metrics: Analyzes metrics from encoders.

# The following areas are blank and require input from the user:
# - Additional error handling logic for specific error types or logging requirements that are not yet defined.
# - Configuration details for retry logic, such as exponential backoff or jitter, that may need customization.
# - Any additional metrics or logging categories that the user might want to track.
# - Specific logic for handling different error types in the `analyze_metrics` method.
# - Detailed implementation for methods like `analyze_streaming_stability`, `analyze_network_health`, etc.

# Levels of abstraction that need to be made specific:
# 1. Error Handling Logic: Define specific logic for handling different types of errors (e.g., network, streaming, recording).
# 2. Retry Logic: Customize and add any additional retry mechanisms, such as exponential backoff or jitter.
# 3. Metrics: Customize and add any additional metrics that need to be tracked.
# 4. Logging: Configure log formatting and output destinations as per the application's requirements.
# 5. Error Analysis: Implement detailed logic for analyzing errors and providing insights.
# 6. Error Entry Creation: Ensure the error data captures all necessary details for each error type.
# 7. Error Processing: Define the specific steps to process and handle each error type in the `analyze_metrics` method.


class MetricsAnalyzer:
    """Consolidated metrics analysis system"""
    
    def __init__(self):
        self.thresholds = {
            'streaming': {
                'bitrate_variance': 0.2,  # 20% variance
                'dropped_frames_max': 100,
                'fps_min': 25
            },
            'network': {
                'packet_loss_threshold': 0.001,  # 0.1%
                'latency_max': 100,  # ms
                'jitter_max': 30  # ms
            },
            'storage': {
                'usage_warning': 0.8,  # 80%
                'growth_rate_max': 0.1,  # 10% per hour
                'health_min': 70
            },
            'system': {
                'cpu_max': 80,  # %
                'memory_max': 85,  # %
                'temperature_max': 80  # Celsius
            }
        }

    @handle_errors()
    async def analyze_metrics(self, metrics: List[EncoderMetrics]) -> Dict:
        """Comprehensive metrics analysis"""
        return {
            'streaming': await self.analyze_streaming_stability(metrics),
            'network': await self.analyze_network_health(metrics),
            'storage': await self.analyze_storage_health(metrics),
            'system': await self.analyze_system_health(metrics),
            'predictions': await self.generate_predictions(metrics)
        }

    async def analyze_streaming_stability(self, metrics: List[EncoderMetrics]) -> Dict:
        """Analyze streaming stability metrics"""
        bitrates = [m.streaming_data.get('bitrate', 0) for m in metrics]
        fps_values = [m.streaming_data.get('fps', 0) for m in metrics]
        dropped_frames = [m.streaming_data.get('dropped_frames', 0) for m in metrics]
        
        return {
            'bitrate_stability': self._calculate_stability(bitrates),
            'fps_stability': self._calculate_stability(fps_values),
            'dropped_frames_total': sum(dropped_frames),
            'quality_score': self._calculate_quality_score(metrics),
            'issues': self._detect_streaming_issues(metrics)
        }

    async def analyze_network_health(self, metrics: List[EncoderMetrics]) -> Dict:
        """Analyze network health metrics"""
        packet_loss = [m.network_stats.get('packet_loss_rate', 0) for m in metrics]
        latencies = [m.network_stats.get('latency_ms', 0) for m in metrics]
        
        return {
            'average_packet_loss': np.mean(packet_loss),
            'max_latency': max(latencies),
            'latency_stability': self._calculate_stability(latencies),
            'network_score': self._calculate_network_score(metrics),
            'issues': self._detect_network_issues(metrics)
        }

    async def generate_predictions(self, metrics: List[EncoderMetrics]) -> Dict:
        """Generate predictions based on historical metrics"""
        return {
            'storage': await self.predict_storage_needs(metrics),
            'performance': await self.predict_performance_trends(metrics),
            'reliability': await self.predict_reliability_score(metrics)
        }

    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability score (0-1) based on variance"""
        if not values:
            return 1.0
        mean = np.mean(values)
        variance = np.var(values)
        return 1.0 / (1.0 + (variance / (mean ** 2)))

    def _detect_issues(self, metrics: List[EncoderMetrics]) -> List[Dict]:
        """Detect issues across all metrics"""
        issues = []
        
        for metric in metrics:
            # Check streaming issues
            if metric.streaming_data.get('dropped_frames', 0) > self.thresholds['streaming']['dropped_frames_max']:
                issues.append({
                    'type': 'streaming',
                    'severity': 'high',
                    'message': 'High dropped frames detected',
                    'timestamp': metric.timestamp
                })
            
            # Check network issues
            if metric.network_stats.get('packet_loss_rate', 0) > self.thresholds['network']['packet_loss_threshold']:
                issues.append({
                    'type': 'network',
                    'severity': 'high',
                    'message': 'High packet loss detected',
                    'timestamp': metric.timestamp
                })
            
            # Add more issue detection logic...
        
        return issues 