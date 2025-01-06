import pytest
from unittest.mock import Mock, patch
import time
from ..services.encoder_backup_fail_over import LoadBalancer, EncoderHealth, StreamingConfig

@pytest.fixture
def load_balancer():
    return LoadBalancer()

@pytest.fixture
def sample_health_metrics():
    return {
        'cpu_usage': 0.5,
        'memory_usage': 0.4,
        'network_load': 0.3,
        'error_rate': 0.01
    }

def test_failover_triggering(load_balancer):
    # Setup initial state
    encoder_id = 1
    backup_id = 2
    load_balancer.failover_groups[encoder_id] = [backup_id]
    
    # Add declining health metrics
    for score in [0.7, 0.65, 0.55]:
        load_balancer.health_history.setdefault(encoder_id, []).append(score)
    
    # Add healthy backup
    load_balancer.encoder_health[backup_id] = EncoderHealth(
        encoder_id=backup_id,
        cpu_usage=0.3,
        memory_usage=0.3,
        network_load=0.3,
        client_count=5,
        error_rate=0.01,
        last_update=time.time()
    )
    
    # Test failover
    assert load_balancer._should_trigger_failover(encoder_id)
    assert load_balancer._initiate_failover(encoder_id)

def test_load_distribution(load_balancer, sample_health_metrics):
    # Add multiple encoders with different loads
    for i in range(3):
        load_balancer.update_encoder_health(i, {
            **sample_health_metrics,
            'client_count': i * 10
        })
    
    distribution = load_balancer._calculate_load_distribution()
    assert 'variance' in distribution
    assert 'imbalance' in distribution
    assert distribution['imbalance'] > 0  # Should detect imbalance

def test_client_migration(load_balancer):
    # Setup source and target encoders
    source_id = 1
    target_id = 2
    
    # Add some clients to source
    for i in range(5):
        load_balancer.client_assignments[f'client_{i}'] = source_id
    
    # Test migration
    success = load_balancer._migrate_clients(source_id, target_id)
    assert success
    
    # Verify all clients moved
    assert all(eid == target_id for eid in load_balancer.client_assignments.values()) 

def test_stream_handoff(load_balancer):
    # Setup encoder group
    primary_id = 1
    backup_id = 2
    config = StreamingConfig(
        rtmp_key="test_key",
        resolution="1920x1080",
        bitrate=5000000,
        fps=30
    )
    
    load_balancer.setup_encoder_group(primary_id, [backup_id], config)
    
    # Mock encoder APIs
    primary_api = Mock()
    backup_api = Mock()
    load_balancer.encoder_apis = {
        primary_id: primary_api,
        backup_id: backup_api
    }
    
    # Test stream handoff
    assert load_balancer._handoff_stream(primary_id, backup_id)
    
    # Verify API calls
    backup_api.configure_streaming.assert_called_once()
    backup_api.start_streaming.assert_called_once()
    primary_api.stop_streaming.assert_called_once()

def test_stream_health_monitoring(load_balancer):
    encoder_id = 1
    api = Mock()
    api.get_streaming_metrics.return_value = {
        'dropped_frames': 150,  # Unhealthy
        'bandwidth': 4000000,
        'target_bitrate': 5000000,  # Below target
        'errors': 1
    }
    
    load_balancer.encoder_apis = {encoder_id: api}
    
    health = load_balancer._check_stream_health(encoder_id)
    assert not health['healthy']
    assert 'high_frame_drop' in health['issues']
    assert 'low_bandwidth' in health['issues']
    assert 'streaming_errors' in health['issues']