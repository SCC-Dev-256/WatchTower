from functools import wraps
from flask_socketio import disconnect
from flask import current_app
import jwt

class WebSocketAuthenticator:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
    def authenticate_socket(self, auth_token):
        try:
            payload = jwt.decode(
                auth_token, 
                self.app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload['sub']
        except jwt.InvalidTokenError:
            return None

def authenticated_socket(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        auth_token = kwargs.get('auth_token')
        if not auth_token:
            disconnect()
            return False
            
        authenticator = current_app.websocket_auth
        user_id = authenticator.authenticate_socket(auth_token)
        if not user_id:
            disconnect()
            return False
            
        return f(*args, **kwargs)
    return wrapped 