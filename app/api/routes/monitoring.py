from flask import Blueprint, jsonify, request
from app.core.error_handling import handle_errors
from WatchTower.app.core.auth.auth import require_api_key
from app.core.security.rbac import roles_required
from app.core.metrics.metrics_service import MetricsService

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')
metrics_service = MetricsService()

@monitoring_bp.route('/status', methods=['GET'])
@require_api_key
@handle_errors()
@roles_required('admin', 'editor', 'viewer')
def get_monitoring_status():
    """Get overall monitoring status"""
    return jsonify(metrics_service.get_system_metrics())

@monitoring_bp.route('/alerts', methods=['GET'])
@require_api_key
@handle_errors()
@roles_required('admin', 'editor', 'viewer')
def get_alerts():
    """Get active alerts"""
    return jsonify(metrics_service.get_active_alerts()) 