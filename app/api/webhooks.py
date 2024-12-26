from flask import Blueprint, current_app, request, jsonify
from functools import wraps
import hmac
import hashlib

webhooks_bp = Blueprint('webhooks', __name__)

def verify_webhook_signature(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Webhook-Signature')
        if not signature:
            return jsonify({'error': 'Missing signature'}), 401
            
        # Verify HMAC signature
        secret = current_app.config['WEBHOOK_SECRET']
        expected = hmac.new(
            secret.encode(),
            request.data,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            return jsonify({'error': 'Invalid signature'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@webhooks_bp.route('/webhooks/encoder-status', methods=['POST'])
@verify_webhook_signature
def handle_encoder_status():
    """Handle encoder status webhooks"""
    data = request.get_json()
    
    # Process webhook
    current_app.notification_manager.process_webhook(
        'encoder_status',
        data
    )
    
    return jsonify({'status': 'processed'}) 