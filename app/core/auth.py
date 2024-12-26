from functools import wraps
from flask import request, jsonify
from app.models.api_key import APIKey
from datetime import datetime

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if not api_key:
            return jsonify({"error": "No API key provided"}), 401
            
        key = api_key.split(" ")[1] if " " in api_key else api_key
        stored_key = APIKey.query.filter_by(key=key).first()
        
        if not stored_key or stored_key.expires_at < datetime.utcnow():
            return jsonify({"error": "Invalid or expired API key"}), 401
            
        return f(*args, **kwargs)
    return decorated_function 