import requests
from typing import Dict
import json
import hmac
import hashlib
from datetime import datetime

class WebhookService:
    def __init__(self, app):
        self.app = app
        self.redis = app.redis_client
        
    def send_webhook(self, url: str, data: Dict, retry: bool = True):
        """Send webhook with signature and retries"""
        payload = {
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        # Generate signature
        signature = hmac.new(
            self.app.config['WEBHOOK_SECRET'].encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-Webhook-Signature': signature
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            if retry:
                self._queue_retry(url, payload)
            return False
            
    def _queue_retry(self, url: str, payload: Dict):
        """Queue failed webhook for retry"""
        self.redis.rpush(
            'webhook_retries',
            json.dumps({
                'url': url,
                'payload': payload,
                'attempts': 0
            })
        ) 