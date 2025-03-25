from flask_socketio import SocketIO, emit, disconnect, request
from datetime import datetime
import asyncio
import logging
from typing import Dict, Any, Set
from collections import defaultdict
from app.core.auditing_log import setup_logging
from app.services.websocket.websocket_auth import WebSocketAuthenticator
from app.core.config.websocket_config import Config
from WatchTower.app.core.auth.auth import require_api_key, roles_required
from app.core.error_handling.decorators import handle_errors
from app.services.websocket.websocket_security import WebSocketSecurity
from app.services.websocket.websocket_rate_limiter import WebSocketRateLimiter
from app.services.encoder_manager import EncoderManager
from app.services.encoder_service import EncoderService

logger = setup_logging(__name__)

class UnifiedWebSocketService:
    def __init__(self, socketio: SocketIO, app=None):
        self.socketio = socketio
        self.app = app
        self.connected_clients: Dict[str, Dict] = {}
        self.encoder_states: Dict[int, Dict] = {}
        self.batch_queue: Dict[str, list] = defaultdict(list)
        self.batch_interval = 0.5  # seconds
        self.logger = setup_logging(__name__)
        self.authenticator = WebSocketAuthenticator(socketio)
        self.security = WebSocketSecurity()
        self.rate_limiter = WebSocketRateLimiter()
        self.encoder_manager = EncoderManager(app.db)  # Assuming app has a db attribute
        self.encoder_service = EncoderService()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self._register_handlers()
        self._start_background_tasks()

    @handle_errors()
    def _register_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            token = request.args.get('token')
            self.on_connect(token)
            
        @self.socketio.on('subscribe_encoder')
        @self.security.secure_websocket
        async def handle_subscription(data):
            client_id = request.sid
            encoder_id = data.get('encoder_id')
            
            try:
                await self._handle_subscription(client_id, encoder_id)
                emit('subscription_success', {'encoder_id': encoder_id})
            except Exception as e:
                logger.error(f"Subscription error: {str(e)}")
                emit('error', {'message': str(e)})

    @handle_errors()
    async def _validate_connection(self, client_id: str) -> bool:
        """Validate new connection with rate limiting and security checks"""
        if not self.rate_limiter.check_rate_limit(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
            
        if len(self.connected_clients) >= self.app.config['MAX_WEBSOCKET_CLIENTS']:
            logger.warning("Maximum client connections reached")
            return False
            
        return True
        
    @handle_errors()
    async def broadcast_update(self, encoder_id: int, update_type: str, data: dict):
        """Queue update for batch processing"""
        self.batch_queue[encoder_id].append({
            'type': update_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    @handle_errors()
    async def _process_batch_queue(self):
        """Process batched updates"""
        while True:
            for encoder_id, updates in self.batch_queue.items():
                if updates:
                    batch = updates.copy()
                    self.batch_queue[encoder_id] = []
                    
                    # Send to subscribed clients
                    for client_id, client in self.connected_clients.items():
                        if encoder_id in client['subscriptions']:
                            try:
                                self.socketio.emit(
                                    'encoder_batch_update',
                                    {
                                        'encoder_id': encoder_id,
                                        'updates': batch
                                    },
                                    room=client_id
                                )
                            except Exception as e:
                                logger.error(f"Failed to send batch: {str(e)}")
                                await self._handle_client_error(client_id)
                                
            await asyncio.sleep(self.batch_interval)

    @handle_errors()
    def _start_background_tasks(self):
        """Start background processing tasks"""
        self.socketio.start_background_task(self._process_batch_queue)
        self.socketio.start_background_task(self._monitor_clients)
        self.socketio.start_background_task(self._monitor_encoders) 

    @handle_errors()
    @roles_required('admin', 'editor', 'viewer')
    @require_api_key
    def on_connect(self, token: str):
        """Handle new WebSocket connection with token authentication."""
        if not self.authenticator.authenticate(token):
            disconnect()  # Disconnect unauthorized clients
            return

        # Proceed with connection setup for authorized clients
        # ...

    async def _handle_subscription(self, client_id: str, encoder_id: str):
        """Handle client subscription to encoder updates"""
        if client_id not in self.connected_clients:
            self.connected_clients[client_id] = {'subscriptions': set()}
        
        self.connected_clients[client_id]['subscriptions'].add(encoder_id)
        self.logger.info(f"Client {client_id} subscribed to encoder {encoder_id}")

    async def _handle_client_error(self, client_id: str):
        """Handle errors related to a specific client"""
        self.logger.error(f"Handling error for client {client_id}")
        if client_id in self.connected_clients:
            disconnect(client_id)
            del self.connected_clients[client_id]

    async def _monitor_clients(self):
        """Monitor connected clients for activity and health"""
        while True:
            for client_id in list(self.connected_clients.keys()):
                # Implement logic to check client activity
                # For example, check if the client has sent a heartbeat recently
                # If not, consider the client disconnected
                if not self._is_client_active(client_id):
                    self.logger.info(f"Client {client_id} is inactive, disconnecting")
                    await self._handle_client_error(client_id)
            
            await asyncio.sleep(10)  # Check every 10 seconds

    def _is_client_active(self, client_id: str) -> bool:
        """Check if a client is active based on the last message timestamp."""
        client_info = self.connected_clients.get(client_id)
        if not client_info:
            return False

        last_message_time = client_info.get('last_message_time')
        if not last_message_time:
            return False

        # Consider the client inactive if no message received in the last 30 seconds
        return (datetime.utcnow() - last_message_time).total_seconds() < 30

    async def _monitor_encoders(self):
        """Monitor encoder states and health"""
        while True:
            for encoder_id in self.encoder_states.keys():
                try:
                    # Retrieve the current state of the encoder
                    encoder = await self.encoder_service._op_get_encoder(encoder_id)
                    new_state = await self.encoder_manager.get_encoder_status(encoder_id)
                    
                    # Check if the state has changed
                    if new_state != self.encoder_states[encoder_id]:
                        self.encoder_states[encoder_id] = new_state
                        await self.broadcast_update(encoder_id, 'state_change', new_state)
                except Exception as e:
                    self.logger.error(f"Error monitoring encoder {encoder_id}: {str(e)}")
            
            await asyncio.sleep(30)  # Check every 30 seconds

