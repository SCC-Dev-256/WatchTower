import pytest
from datetime import datetime, timedelta
from app.core.error_handling.analysis.system import MetricsSystem

@pytest.fixture
async def metrics_system(app):
    return MetricsSystem(app)

async def test_metrics_collection(metrics_system):
    encoder_id = "test_encoder"
    result = await metrics_system.collect_and_analyze(encoder_id)
    
    assert 'metrics' in result
    assert 'analysis' in result
    assert 'timestamp' in result
    
    metrics = result['metrics']
    assert 'streaming' in metrics
    assert 'bandwidth' in metrics
    assert 'storage' in metrics

async def test_historical_analysis(metrics_system):
    encoder_id = "test_encoder"
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    history = await metrics_system.get_historical_metrics(
        encoder_id,
        start_time,
        end_time
    )
    
    assert isinstance(history, list)
    assert all('timestamp' in m for m in history) 