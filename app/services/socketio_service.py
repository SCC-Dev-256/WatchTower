from flask_socketio import SocketIO, emit, disconnect
from flask import current_app, request
from app.core.database.models.encoder import Encoder
from ..core.metrics.metrics_analyzer import MetricsAnalyzer
from app.core.error_handling import handle_errors
from app.core.error_handling.errors import APIError, EncoderError
from datetime import datetime
import time
from app.core.database.models.encoder import Encoder
from app.core.database.models.encoder import EncoderMetrics
from app.core.database.models.notification_model import NotificationSettings, NotificationRule
from app.core.database.models.api_key_management import APIKey
from app.core.database.models.log_entry import LogEntry
from WatchTower.app.core.auth.auth import require_api_key, roles_required
from app.core.error_handling.decorators import handle_errors
from app.core.metrics.metrics_analyzer import MetricsAnalyzer
from app.services.websocket.websocket_security import WebSocketSecurity
from app.services.websocket.websocket_rate_limiter import WebSocketRateLimiter
from app.services.websocket.websocket_auth import Authenticator
from app.services.encoder_backup_fail_over import LoadBalancer
from app.services.performance_monitor import PerformanceMonitor


class EnhancedSocketIOService:
    def __init__(self, app=None):
        self.socketio = SocketIO()
        self.connected_clients = {}
        self.metrics_analyzer = MetricsAnalyzer()
        self.security = WebSocketSecurity()
        self.performance_monitor = PerformanceMonitor()
        self.load_balancer = LoadBalancer()
        self.rate_limiter = WebSocketRateLimiter()
        self.authenticator = Authenticator()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.socketio.init_app(app)
        self.authenticator.init_app(app)
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        @self.socketio.on('connect')
        @require_api_key
        @handle_errors()
        @roles_required('admin', 'editor')
        def handle_connect(auth_token):
            client_id = request.sid
            if not self.rate_limiter.check_rate_limit(client_id):
                disconnect()
                return False
                
            # Initialize client connection
            self._initialize_client(client_id)
            
        @self.socketio.on('subscribe_encoder')
        @require_api_key
        @handle_errors()
        @roles_required('admin', 'editor')
        def handle_subscription(data, auth_token):
            client_id = request.sid
            if not self.rate_limiter.check_rate_limit(client_id):
                emit('error', {'message': 'Rate limit exceeded'})
                return
                
            encoder_id = data.get('encoder_id')
            self._handle_subscription(client_id, encoder_id)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = request.sid
            self.connected_clients.pop(client_id, None)
        
        @self.socketio.on('performance_metrics')
        @self.security.secure_websocket
        def handle_performance_metrics(data):
            """Handle client performance metrics"""
            client_id = request.sid
            if client_id in self.connected_clients:
                self.performance_monitor.record_client_metrics(client_id, data)
        
        # Add periodic load balancing check
        def check_load_balance():
            moves = self.load_balancer.rebalance_if_needed()
            for client_id, old_encoder, new_encoder in moves:
                try:
                    # Notify client of reassignment
                    self.socketio.emit('encoder_reassigned', {
                        'new_encoder_id': new_encoder
                    }, room=client_id)
                    
                    # Update client assignment
                    if client_id in self.connected_clients:
                        self.connected_clients[client_id]['assigned_encoder'] = new_encoder
                        self.connected_clients[client_id]['subscriptions'].add(new_encoder)
                except Exception as e:
                    current_app.logger.error(
                        f"Failed to reassign client {client_id}: {str(e)}"
                    )
        
        # Run load balance check every 30 seconds
        self.socketio.start_background_task(
            target=lambda: self.socketio.sleep(30) or check_load_balance()
        )
    
    def broadcast_encoder_update(self, encoder_id: int, data: dict):
        """Broadcast updates to subscribed clients"""
        try:
            # Add analysis to the data
            data['analysis'] = self.metrics_analyzer.analyze_streaming_stability(data)
            
            # Broadcast to subscribed clients only
            for client_id, subscriptions in self.connected_clients.items():
                if encoder_id in subscriptions['subscriptions']:
                    try:
                        self.socketio.emit('encoder_update', data, room=client_id)
                    except Exception as e:
                        raise EncoderError(f"Failed to send update", encoder_id=str(encoder_id))
        except Exception as e:
            raise APIError(f"Broadcast failed: {str(e)}", code=500)
    
    def _handle_client_error(self, client_id: str):
        """Handle problematic client connections"""
        try:
            current_app.logger.warning(f"Disconnecting problematic client: {client_id}")
            try:
                self.connected_clients.pop(client_id, None)
                disconnect(client_id)
            except Exception as e:
                raise APIError(f"Failed to disconnect client: {str(e)}", code=500)
        except Exception as e:
            raise APIError(f"Client error handling failed: {str(e)}", code=500)
    
    def _get_encoder_data(self, encoder_id: int) -> dict:
        """Get encoder data with error handling and retries"""
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                encoder = Encoder.query.get(encoder_id)
                if not encoder:
                    raise ValueError(f"Encoder {encoder_id} not found")
                
                metrics = self.metrics_analyzer.get_current_metrics(encoder)
                analysis = self.metrics_analyzer.analyze_streaming_stability(metrics)
                
                return {
                    'metrics': metrics,
                    'analysis': analysis,
                    'timestamp': datetime.utcnow().isoformat(),
                    'sequence': self._get_next_sequence()
                }
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    current_app.logger.error(f"Failed to get encoder data after {max_retries} attempts: {str(e)}")
                    raise
                time.sleep(1)  # Wait before retry
    
    def _get_next_sequence(self) -> int:
        """Get next sequence number for message ordering"""
        if not hasattr(self, '_sequence'):
            self._sequence = 0
        self._sequence += 1
        return self._sequence
    
    def handle_client_message(self, client_id: str, message_type: str, data: dict):
        """Handle incoming client messages with validation"""
        try:
            if message_type not in self.message_handlers:
                raise ValueError(f"Unknown message type: {message_type}")
            
            handler = self.message_handlers[message_type]
            return handler(client_id, data)
        except Exception as e:
            current_app.logger.error(f"Error handling client message: {str(e)}")
            self.send_error(client_id, str(e))
    
    def send_error(self, client_id: str, error_message: str):
        """Send error message to client"""
        try:
            self.socketio.emit('error', {
                'message': error_message,
                'timestamp': datetime.utcnow().isoformat()
            }, room=client_id)
        except Exception as e:
            current_app.logger.error(f"Failed to send error to client {client_id}: {str(e)}")