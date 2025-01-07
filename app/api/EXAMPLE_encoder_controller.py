from flask import Blueprint, jsonify
from app.core.monitoring.system_monitor import MonitoringSystem

encoder_bp = Blueprint('encoder', __name__)

@encoder_bp.route('/status/<encoder_id>', methods=['GET'])
async def get_encoder_status(encoder_id):
    monitoring_system = MonitoringSystem()
    status = await monitoring_system.monitor_encoder(encoder_id)
    return jsonify(status)

#Example Update in a Controller
#If a controller or API endpoint is collecting metrics, update it to use SystemMonitor