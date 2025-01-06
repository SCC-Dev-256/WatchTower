from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
from app.core.database.models.encoder import Encoder
from app.core.database.models.encoder_metric import EncoderMetrics

class MetricsAnalyzer:
    def __init__(self):
        self.anomaly_thresholds = {
            'bitrate_variance': 0.2,  # 20% variance
            'packet_loss_threshold': 0.001,  # 0.1%
            'storage_growth_rate': 0.1,  # 10% per hour
            'temperature_max': 80  # Celsius
        }

    def analyze_streaming_stability(self, metrics: List[EncoderMetrics]) -> Dict:
        """Analyze streaming stability over time"""
        bitrates = [m.streaming_data['bitrate'] for m in metrics]
        fps_values = [m.streaming_data['fps'] for m in metrics]
        
        return {
            'bitrate_stability': self._calculate_stability(bitrates),
            'fps_stability': self._calculate_stability(fps_values),
            'dropped_frames_total': sum(m.streaming_data.get('dropped_frames', 0) for m in metrics),
            'quality_score': self._calculate_quality_score(metrics)
        }

    def analyze_network_health(self, metrics: List[EncoderMetrics]) -> Dict:
        """Analyze network health metrics"""
        packet_loss_rates = [m.network_stats['packet_loss_rate'] for m in metrics]
        latencies = [m.network_stats['latency_ms'] for m in metrics]
        
        return {
            'average_packet_loss': np.mean(packet_loss_rates),
            'max_latency': max(latencies),
            'latency_stability': self._calculate_stability(latencies),
            'network_score': self._calculate_network_score(metrics)
        }

    def predict_storage_needs(self, metrics: List[EncoderMetrics], hours: int = 24) -> Dict:
        """Predict storage requirements"""
        storage_usage = [(m.timestamp, m.storage['used']) for m in metrics]
        growth_rate = self._calculate_growth_rate(storage_usage)
        
        return {
            'current_usage': metrics[-1].storage['used'],
            'hourly_growth_rate': growth_rate,
            'predicted_usage_24h': metrics[-1].storage['used'] + (growth_rate * 24),
            'time_until_full': self._estimate_time_until_full(
                metrics[-1].storage['used'],
                metrics[-1].storage['total'],
                growth_rate
            )
        }

    def _calculate_stability(self, values: List[float]) -> float:
        """Calculate stability score (0-1) based on variance"""
        if not values:
            return 1.0
        mean = np.mean(values)
        variance = np.var(values)
        return 1.0 / (1.0 + (variance / (mean ** 2)))

    def _calculate_quality_score(self, metrics: List[EncoderMetrics]) -> float:
        """Calculate overall quality score (0-100)"""
        scores = []
        
        # Bitrate stability
        bitrate_stability = self._calculate_stability(
            [m.streaming_data['bitrate'] for m in metrics]
        )
        scores.append(bitrate_stability * 100)
        
        # Frame drops
        total_frames = sum(m.streaming_data.get('total_frames', 0) for m in metrics)
        dropped_frames = sum(m.streaming_data.get('dropped_frames', 0) for m in metrics)
        if total_frames > 0:
            frame_score = 100 * (1 - (dropped_frames / total_frames))
            scores.append(frame_score)
        
        return np.mean(scores) if scores else 0 