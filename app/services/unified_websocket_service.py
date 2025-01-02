from flask_socketio import SocketIO, emit, disconnect, request
from datetime import datetime
import asyncio
import logging
from typing import Dict, Any, Set
from collections import defaultdict
from app.core.logging import setup_logging
from app.services.websocket_auth import WebSocketAuthenticator
from app.core.config.websocket_config import Config

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
        
    def init_app(self, app):
        self.app = app
        self._register_handlers()
        self._start_background_tasks()
        
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
                
    async def _validate_connection(self, client_id: str) -> bool:
        """Validate new connection with rate limiting and security checks"""
        if not self.rate_limiter.check_rate_limit(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
            
        if len(self.connected_clients) >= self.app.config['MAX_WEBSOCKET_CLIENTS']:
            logger.warning("Maximum client connections reached")
            return False
            
        return True
        
    async def broadcast_update(self, encoder_id: int, update_type: str, data: dict):
        """Queue update for batch processing"""
        self.batch_queue[encoder_id].append({
            'type': update_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
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
            
    def _start_background_tasks(self):
        """Start background processing tasks"""
        self.socketio.start_background_task(self._process_batch_queue)
        self.socketio.start_background_task(self._monitor_clients)
        self.socketio.start_background_task(self._monitor_encoders) 

    def on_connect(self, token: str):
        """Handle new WebSocket connection with token authentication."""
        if not self.authenticator.authenticate(token):
            disconnect()  # Disconnect unauthorized clients
            return

        # Proceed with connection setup for authorized clients
        # ... 