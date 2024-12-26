from prometheus_client import Gauge, Counter, Histogram

class EncoderHealthMetrics:
    """Consolidated health monitoring metrics"""
    
    # Device Status Metrics
    device_health = Gauge(
        'encoder_device_health',
        'Overall device health score',
        ['encoder_id', 'metric_type']
    )
    
    # Connection Metrics
    connection_health = Gauge(
        'encoder_connection_health',
        'Connection health score',
        ['encoder_id', 'connection_id']
    )
    
    # Performance Metrics
    performance_metrics = {
        'cpu_usage': Gauge(
            'encoder_cpu_usage',
            'CPU usage percentage',
            ['encoder_id']
        ),
        'memory_usage': Gauge(
            'encoder_memory_usage',
            'Memory usage percentage',
            ['encoder_id']
        ),
        'temperature': Gauge(
            'encoder_temperature',
            'Device temperature in Celsius',
            ['encoder_id']
        )
    }
    
    # Stream Health Metrics
    stream_metrics = {
        'bitrate': Gauge(
            'encoder_stream_bitrate',
            'Current stream bitrate',
            ['encoder_id', 'stream_id']
        ),
        'dropped_frames': Counter(
            'encoder_dropped_frames_total',
            'Total dropped frames',
            ['encoder_id', 'stream_id']
        ),
        'stream_errors': Counter(
            'encoder_stream_errors_total',
            'Stream error count',
            ['encoder_id', 'error_type']
        )
    }
    
    # Health Check Metrics
    health_check_metrics = {
        'checks_total': Counter(
            'encoder_health_checks_total',
            'Total health checks performed',
            ['encoder_id', 'check_type']
        ),
        'check_duration': Histogram(
            'encoder_health_check_duration_seconds',
            'Health check duration',
            ['encoder_id', 'check_type']
        ),
        'check_failures': Counter(
            'encoder_health_check_failures_total',
            'Health check failures',
            ['encoder_id', 'failure_reason']
        )
    } 