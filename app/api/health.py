from flask import Blueprint, jsonify
from app.monitoring.health_check import HealthCheckService
from app.core.auth import require_api_key, roles_required
from app.core.errors import error_handler

health_bp = Blueprint('health', __name__)
health_service = HealthCheckService()

@health_bp.route('/health/encoder/<int:encoder_id>', methods=['GET'])
@roles_required('admin', 'editor', 'viewer')
@require_api_key
@error_handler
async def get_encoder_health(encoder_id: int):
    """Get health status of a specific encoder."""
    health_data = await health_service.check_encoder_health(encoder_id)
    return jsonify(health_data)

@health_bp.route('/health/detailed', methods=['GET'])
@roles_required('admin', 'editor', 'viewer')
@require_api_key
@error_handler
async def get_detailed_health():
    """Get detailed health status of all encoders."""
    health_data = await health_service.check_all_encoders()
    return jsonify(health_data) 