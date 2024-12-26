from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
from app.core.connection.health_checker import ConnectionHealthChecker
from app.core.connection.thermal_manager import ConnectionThermalManager
from app.core.rest_API_client import AJADevice
from app.models.encoder import HeloEncoder

health_bp = Blueprint('health', __name__)

@health_bp.route('/health/encoder/<int:encoder_id>')
async def encoder_health(encoder_id):
    """
    Get comprehensive encoder health status combining both direct API checks
    and connection health monitoring.
    
    Benefits of dual monitoring:
    1. Direct API: Immediate device state
    2. Connection Health: Historical patterns and predictive insights
    3. Thermal Management: Prevents overload before it impacts encoding
    """
    # Get direct encoder status
    encoder = HeloEncoder.query.get(encoder_id)
    device = AJADevice(f"http://{encoder.ip_address}")
    
    # Get direct API metrics
    direct_status = await device.get_system_status()
    
    # Get connection health metrics
    health_checker = ConnectionHealthChecker(
        thermal_manager=current_app.thermal_manager,
        db_session=current_app.db.session,
        redis_client=current_app.redis_client
    )
    
    connection_health = await health_checker.get_detailed_health(str(encoder_id))
    
    # Combine both monitoring approaches
    return jsonify({
        "timestamp": datetime.utcnow().isoformat(),
        "encoder": {
            # Direct API metrics
            "device_status": {
                "cpu_usage": direct_status.get("cpu_usage"),
                "memory_usage": direct_status.get("memory_usage"),
                "temperature": direct_status.get("temperature"),
                "fan_speed": direct_status.get("fan_speed"),
                "uptime": direct_status.get("uptime")
            },
            # Streaming status direct from device
            "streaming": {
                "active": await device.get_param("eParamID_ReplicatorStreamState"),
                "bitrate": await device.get_param("eParamID_ReplicatorBitrate"),
                "format": await device.get_param("eParamID_ReplicatorFormat")
            },
            # Connection health and thermal management
            "connection_health": connection_health,
            # Additional metrics from health checker
            "historical_performance": await health_checker.get_performance_history(str(encoder_id)),
            "thermal_status": await current_app.thermal_manager.get_thermal_status(str(encoder_id))
        }
    })

@health_bp.route('/health/detailed')
async def detailed_health():
    """
    Get detailed system and encoder health status combining both 
    direct API access and connection monitoring.
    """
    health_checker = ConnectionHealthChecker(
        thermal_manager=current_app.thermal_manager,
        db_session=current_app.db.session,
        redis_client=current_app.redis_client
    )
    
    # Get system metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get health for all encoders
    encoder_health = {}
    for encoder in current_app.encoder_manager.get_all_encoders():
        # Get direct encoder status
        device = AJADevice(f"http://{encoder.ip_address}")
        direct_status = await device.get_system_status()
        
        # Combine direct and connection health
        encoder_health[encoder.id] = {
            "device_status": direct_status,
            "connection_health": await health_checker.get_detailed_health(str(encoder.id)),
            "thermal_status": await current_app.thermal_manager.get_thermal_status(str(encoder.id))
        }
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'system': {
            'cpu_percent': psutil.cpu_percent(),
            'memory_used_percent': memory.percent,
            'disk_used_percent': disk.percent,
        },
        'services': {
            'database': health_checker._check_database(),
            'redis': health_checker._check_redis(),
        },
        'encoders': encoder_health
    }) 