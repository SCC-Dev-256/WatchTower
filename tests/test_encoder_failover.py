import pytest
from unittest.mock import AsyncMock, patch
from app.services.encoder_backup_fail_over import LoadBalancer
from app.encoder_schemas.encoder import EncoderSchema
from app.core.aja.aja_device import AJADevice
from app.core.aja.aja_constants import AJAParameters

@pytest.mark.asyncio
async def test_encoder_failover():
    # Mock the encoder service and metrics collector
    encoder_service_mock = AsyncMock()
    metrics_collector_mock = AsyncMock()

    # Create a LoadBalancer instance with mocked dependencies
    load_balancer = LoadBalancer(metrics_collector=metrics_collector_mock)
    load_balancer.encoder_service = encoder_service_mock

    # Setup mock encoders
    primary_encoder = EncoderSchema(name='PrimaryEncoder', ip_address='192.168.1.10')
    backup_encoder = EncoderSchema(name='BackupEncoder', ip_address='192.168.1.11')

    # Mock the encoder service to return encoders
    encoder_service_mock.get_encoder.side_effect = [primary_encoder, backup_encoder]

    # Mock the metrics collector to simulate failover conditions
    metrics_collector_mock.get_stream_health.return_value = {
        'healthy': False,
        'issues': ['high_frame_drop']
    }

    # Add encoders to failover groups
    load_balancer.failover_groups = {
        primary_encoder.name: {
            'active_streams': {primary_encoder.name},
            'streaming_config': {
                'rtmp_key': 'test_key',
                'resolution': '1080p',
                'bitrate': '4000k',
                'fps': 30
            }
        }
    }

    # Simulate failover
    with patch.object(load_balancer, '_initiate_failover', return_value=True) as mock_failover:
        await load_balancer.monitor_stream_health()

    # Verify failover was initiated
    mock_failover.assert_called_once_with(primary_encoder.name)

    # Verify stream keys were transferred
    encoder_service_mock.get_encoder.assert_any_call(primary_encoder.name)
    encoder_service_mock.get_encoder.assert_any_call(backup_encoder.name)

    # Verify backup encoder is now active
    assert backup_encoder.name in load_balancer.failover_groups[primary_encoder.name]['active_streams']
