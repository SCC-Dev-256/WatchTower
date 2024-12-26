from flask import current_app
from flask_socketio import SocketIO, emit
from datetime import datetime
import json

def init_websocket(app):
    socketio = SocketIO(app)
    
    @socketio.on('connect')
    def handle_connect():
        emit('connection_status', {'status': 'connected'})
    
    @socketio.on('request_metrics')
    def handle_metrics_request():
        metrics = get_current_metrics()
        emit('metrics_update', metrics)
    
    def get_current_metrics():
        encoders = current_app.update_encoder_metrics()
        return {
            'streaming': {
                'timestamp': datetime.now().isoformat(),
                'active_streams': sum(1 for e in encoders if e.streaming_state),
                'encoders': [
                    {
                        'name': e.name,
                        'streaming': e.streaming_state,
                        'bandwidth': e.bandwidth_usage
                    } for e in encoders
                ]
            },
            'bandwidth': {
                'total': sum(e.bandwidth_usage for e in encoders),
                'per_encoder': {
                    e.name: e.bandwidth_usage for e in encoders
                }
            },
            'storage': {
                'total_space': sum(e.storage_total for e in encoders),
                'used_space': sum(e.storage_used for e in encoders),
                'health_status': {
                    e.name: e.storage_health for e in encoders
                }
            }
        }
    
    # Broadcast metrics every 5 seconds
    def broadcast_metrics():
        while True:
            metrics = get_current_metrics()
            socketio.emit('metrics_update', metrics)
            socketio.sleep(5)
    
    socketio.start_background_task(broadcast_metrics)
    
    return socketio 