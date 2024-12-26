from flask import Blueprint, current_app, render_template
from ..monitoring.error_tracking import ErrorTracker
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

# AJA-specific error patterns
AJA_ERROR_PATTERNS = {
    'video_signal_loss': {
        'pattern': r'Video signal lost on input',
        'severity': 'critical',
        'category': 'input',
        'mitigation': ['Check SDI cable connection', 'Verify source output']
    },
    'storage_corruption': {
        'pattern': r'Storage.*corrupt|Invalid.*block',
        'severity': 'critical',
        'category': 'storage',
        'mitigation': ['Initiate storage mitigation', 'Check filesystem']
    },
    'network_timeout': {
        'pattern': r'Network timeout|Connection refused',
        'severity': 'warning',
        'category': 'network',
        'mitigation': ['Check network connectivity', 'Verify DHCP settings']
    },
    'stream_key_invalid': {
        'pattern': r'Invalid stream key|Authentication failed',
        'severity': 'warning',
        'category': 'streaming',
        'mitigation': ['Verify stream key', 'Check service credentials']
    },
    'audio_sync_loss': {
        'pattern': r'Audio sync lost|Audio PTS discontinuity',
        'severity': 'warning',
        'category': 'audio',
        'mitigation': [
            'Check audio source',
            'Verify SDI embedded audio',
            'Check audio settings'
        ]
    },
    'recording_failure': {
        'pattern': r'Recording failed|Write error|Buffer overflow',
        'severity': 'critical',
        'category': 'recording',
        'mitigation': [
            'Check storage space',
            'Verify write permissions',
            'Check storage health'
        ]
    },
    'thermal_warning': {
        'pattern': r'Temperature warning|Thermal threshold',
        'severity': 'warning',
        'category': 'hardware',
        'mitigation': [
            'Check ventilation',
            'Clean air vents',
            'Verify ambient temperature'
        ]
    },
    'stream_bitrate_unstable': {
        'pattern': r'Bitrate fluctuation|Encoding overload',
        'severity': 'warning',
        'category': 'streaming',
        'mitigation': [
            'Check network bandwidth',
            'Adjust bitrate settings',
            'Monitor CPU usage'
        ]
    },
    'ntp_sync_failure': {
        'pattern': r'NTP sync failed|Clock drift detected',
        'severity': 'warning',
        'category': 'system',
        'mitigation': [
            'Check NTP server accessibility',
            'Verify network timeserver',
            'Check timezone settings'
        ]
    }
}

@dashboard_bp.route('/dashboard')
def dashboard():
    # Get metrics
    metrics = current_app.update_encoder_metrics()
    
    # Get recent alerts
    alerts = current_app.error_tracker.get_active_alerts()
    
    # Process metrics for display
    processed_metrics = {
        'total': len(metrics['encoders']),
        'online': sum(1 for e in metrics['encoders'] if e['status'] == 'online'),
        'errors': len(alerts),
        'storage_health': calculate_storage_health(metrics['encoders'])
    }
    
    return render_template('dashboard.html', 
                         metrics=processed_metrics,
                         alerts=alerts)

def calculate_storage_health(encoders):
    """Calculate overall storage health percentage"""
    if not encoders:
        return 0
        
    total_health = sum(
        encoder.get('storage', {}).get('health', 0) 
        for encoder in encoders
    )
    return round(total_health / len(encoders)) 