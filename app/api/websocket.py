from flask_socketio import SocketIO, emit

def init_websocket(app):
    socketio = SocketIO(app)
    
    def status_change_callback(event_data):
        """Broadcast status changes to connected clients"""
        emit('encoder_status', event_data, broadcast=True)
    
    # Subscribe to encoder events
    app.encoder_events.subscribe_to_events(status_change_callback)
    
    return socketio 