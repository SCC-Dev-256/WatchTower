from flask import Blueprint, jsonify
from ..core.error_handler import handle_api_errors
from ..services.load_balancer import LoadBalancer

monitoring_bp = Blueprint('monitoring', __name__)
load_balancer = LoadBalancer()

@monitoring_bp.route('/monitoring/load-balancer', methods=['GET'])
@handle_api_errors
def get_load_balancer_status():
    """Get current load balancer status"""
    metrics = load_balancer.get_load_balancer_metrics()
    return jsonify(metrics)

@monitoring_bp.route('/monitoring/load-balancer/distribution', methods=['GET'])
@handle_api_errors
def get_load_distribution():
    """Get detailed load distribution metrics"""
    distribution = load_balancer._calculate_load_distribution()
    return jsonify(distribution)

@monitoring_bp.route('/monitoring/load-balancer/health', methods=['GET'])
@handle_api_errors
def get_encoder_health():
    """Get health status of all encoders"""
    health_metrics = {
        eid: {
            'current_score': load_balancer._calculate_load_score(health),
            'history': load_balancer.health_history.get(eid, []),
            'status': 'healthy' if load_balancer._calculate_load_score(health) < load_balancer.health_threshold else 'unhealthy'
        }
        for eid, health in load_balancer.encoder_health.items()
    }
    return jsonify(health_metrics)

@monitoring_bp.route('/monitoring/streams/health', methods=['GET'])
@handle_api_errors
def get_stream_health():
    """Get health status of all active streams"""
    stream_health = {}
    
    for encoder_id, group in load_balancer.failover_groups.items():
        if encoder_id in group['active_streams']:
            health = load_balancer._check_stream_health(encoder_id)
            stream_health[encoder_id] = {
                'status': 'healthy' if health['healthy'] else 'unhealthy',
                'issues': health.get('issues', []),
                'metrics': health.get('metrics', {}),
                'backup_available': bool(group['backup_ids']),
                'last_config_sync': group['last_sync'].isoformat() if group['last_sync'] else None
            }
    
    return jsonify(stream_health)

@monitoring_bp.route('/monitoring/streams/config/<int:encoder_id>', methods=['GET'])
@handle_api_errors
def get_stream_config(encoder_id):
    """Get streaming configuration for encoder group"""
    group = load_balancer.failover_groups.get(encoder_id)
    if not group:
        return jsonify({'error': 'Encoder group not found'}), 404
    
    config = group['streaming_config']
    return jsonify({
        'primary_id': encoder_id,
        'backup_ids': group['backup_ids'],
        'active_streams': list(group['active_streams']),
        'config': {
            'resolution': config.resolution,
            'bitrate': config.bitrate,
            'fps': config.fps
        }
    }) 