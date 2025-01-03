from typing import Dict
from app.core.base_service import BaseService
from flask_socketio import SocketIO
from app.core.config import Config
from app.core.error_handling.analysis.correlation_analyzer import ErrorAnalyzer
from app.core.error_handling.decorators import handle_errors
from app.services.metrics_analyzer import MetricsAnalyzer

class NotificationService(BaseService):
    def __init__(self, socketio: SocketIO):
        super().__init__()
        self.socketio = socketio
        self.connected_clients = {}
        self.config = Config()

    @handle_errors()
    async def _op_broadcast_encoder_update(self, encoder_id: str, data: Dict) -> None:
        """Broadcast encoder updates to cablecasters"""
        try:
            # Add metrics analysis if available
            if self.config.get('METRICS_ANALYSIS_ENABLED'):
                # Analyze streaming stability and network health
                metrics_analyzer = MetricsAnalyzer()
                data['analysis'] = {
                    'streaming': metrics_analyzer.analyze_streaming_stability([data['metrics']]),
                    'network': metrics_analyzer.analyze_network_health([data['metrics']]),
                    'storage': metrics_analyzer.predict_storage_needs([data['metrics']]),
                    'error_analysis': ErrorAnalyzer(self.app).analyze_error({
                        'encoder_id': data.get('encoder_id'),
                        'message': data.get('message', ''),
                        'timestamp': data.get('timestamp')
                    })
                }
            
            # Broadcast to cablecasters
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