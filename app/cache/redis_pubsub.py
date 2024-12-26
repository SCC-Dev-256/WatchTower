import json
from datetime import datetime

class EncoderEvents:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.pubsub = self.redis.pubsub()
        
    def publish_status_change(self, encoder_id, status):
        """Publish encoder status changes"""
        self.redis.publish(
            'encoder_events',
            json.dumps({
                'encoder_id': encoder_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat()
            })
        )
    
    def subscribe_to_events(self, callback):
        """Subscribe to encoder events"""
        self.pubsub.subscribe('encoder_events')
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                callback(json.loads(message['data'])) 