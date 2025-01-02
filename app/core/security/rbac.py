from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

def role_required(required_role):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user_role = current_user.get('role', 'guest')  # Default to 'guest' if no role is found

            if user_role != required_role:
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator 