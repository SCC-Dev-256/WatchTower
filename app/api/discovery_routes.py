from flask import Blueprint, jsonify, current_app, request
from app.core.device_discovery import HeloDiscovery, StreamingState
import asyncio
from datetime import datetime
from ..core.security.security_logger import SecurityEventLogger

discovery_bp = Blueprint('discovery', __name__)

@discovery_bp.route('/scan', methods=['POST'])
async def scan_network():
    """Endpoint to trigger network scan for Helo devices"""
    try:
        discovery = HeloDiscovery(current_app.endpoint_registry)
        network_range = current_app.config.get('NETWORK_RANGE', '192.168.1.0/24')
        
        devices = await discovery.scan_network(network_range)
        
        # Log scan event
        SecurityEventLogger(current_app).log_event(
            'device_scan',
            f"Found {len(devices)} devices in network {network_range}"
        )
        
        return jsonify({
            'status': 'success',
            'devices_found': len(devices),
            'devices': devices
        })
    except Exception as e:
        current_app.logger.error(f"Scan failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@discovery_bp.route('/devices/status', methods=['GET'])
def get_device_states():
    """Get current state of all devices with failover status"""
    try:
        discovery = current_app.device_discovery
        states = {}
        
        for ip, status in discovery.encoder_states.items():
            states[ip] = {
                'state': status.state.value,
                'streaming': status.streaming,
                'recording': status.recording,
                'last_error': status.last_error,
                'failover_available': _check_failover_available(ip),
                'last_seen': discovery.known_devices.get(ip).isoformat(),
                'config_version': status.config_version
            }
            
        return jsonify({
            'status': 'success',
            'states': states
        })
    except Exception as e:
        current_app.logger.error(f"Status check failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@discovery_bp.route('/devices/<ip>/failover', methods=['POST'])
async def trigger_failover():
    """Trigger failover for a specific device"""
    try:
        ip = request.view_args['ip']
        discovery = current_app.device_discovery
        
        if ip not in discovery.encoder_states:
            return jsonify({'status': 'error', 'message': 'Device not found'}), 404
            
        # Attempt failover
        success = await discovery.handle_failover(ip)
        
        if success:
            SecurityEventLogger(current_app).log_event(
                'failover_triggered',
                f"Failover successful for device {ip}"
            )
            return jsonify({'status': 'success', 'message': 'Failover completed'})
        else:
            return jsonify({'status': 'error', 'message': 'Failover failed'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Failover failed: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def _check_failover_available(ip: str) -> bool:
    """Check if failover is available for a device"""
    try:
        discovery = current_app.device_discovery
        status = discovery.encoder_states.get(ip)
        
        if not status or status.state == StreamingState.ERROR:
            return False
            
        # Check for available backup devices
        backup_devices = [
            device for device in discovery.known_devices.keys()
            if device != ip and discovery.encoder_states.get(device).state == StreamingState.IDLE
        ]
        
        return len(backup_devices) > 0
    except Exception:
        return False

@discovery_bp.route('/devices', methods=['GET'])
def list_devices():
    """List all known devices"""
    try:
        from app.models.encoder import HeloEncoder
        encoders = HeloEncoder.query.all()
        
        return jsonify({
            'status': 'success',
            'devices': [e.to_dict() for e in encoders]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 