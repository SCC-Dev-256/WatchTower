import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.services.metrics_collector import MetricsCollector
from app.models.encoder import Encoder
from app.models.metrics import EncoderMetrics

@pytest.fixture
def app():
    from flask import Flask
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def collector(app):
    return MetricsCollector(app)

@pytest.fixture
def sample_metrics():
    return {
        'streaming_data': {
            'bitrate': 5000000,
            'fps': 30,
            'dropped_frames': 0
        },
        'network_stats': {
            'packet_loss_rate': 0.0,
            'latency_ms': 50
        },
        'storage': {
            'used': 50000000000,
            'total': 100000000000,
            'write_speed_mbps': 100
        }
    }

def test_analyze_streaming_quality(collector, sample_metrics):
    encoder = Mock(spec=Encoder)
    encoder.id = 1
    
    # Test normal conditions
    collector._analyze_streaming_quality(sample_metrics)
    assert len(collector.alerts) == 0
    
    # Test dropped frames detection
    metrics = sample_metrics.copy()
    metrics['streaming_data']['dropped_frames'] = 10
    collector._analyze_streaming_quality(metrics)
    assert len(collector.alerts) == 1
    assert collector.alerts[0]['type'] == 'dropped_frames_detected' 