from typing import Dict
from app.core.base_service import BaseService
from flask_socketio import SocketIO
from app.core.error_handling import handle_errors

class NotificationService(BaseService):
    def __init__(self, socketio: SocketIO):
        super().__init__()
        self.socketio = socketio
        self.connected_clients = {}

    @handle_errors()
    async def _op_broadcast_encoder_update(self, encoder_id: str, data: Dict) -> None:
        """Broadcast encoder updates to subscribed clients"""
        try:
            # Add metrics analysis if available
            if self.config.get('METRICS_ANALYSIS_ENABLED'):
                data['analysis'] = await self._analyze_metrics(data)
            
            # Broadcast to subscribed clients
            for client_id, subscriptions in self.connected_clients.items():
                if encoder_id in subscriptions.get('subscriptions', []):
                    self.socketio.emit('encoder_update', data, room=client_id)
                    
        except Exception as e:
            self.logger.error(f"Broadcast error for encoder {encoder_id}: {str(e)}")
            raise

    async def _analyze_metrics(self, data: Dict) -> Dict:
        """Analyze metrics data"""
        if 'metrics' not in data:
            return {}
            
        return {
            'stream_health': self._calculate_stream_health(data['metrics']),
            'performance_score': self._calculate_performance(data['metrics'])
        }