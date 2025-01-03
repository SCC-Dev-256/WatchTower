from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.core.security.role_manager import RoleManager
from app.core.security.security_logger import SecurityEventLogger
from app.core.security.models import Role, Permission

security_logger = SecurityEventLogger()
role_manager = RoleManager()

def roles_required(*required_roles):
    """Decorator to enforce role-based access control with multiple roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user_roles = current_user.get('roles', ['guest'])  # Default to 'guest' if no roles are found

            if not any(role in user_roles for role in required_roles):
                security_logger.log_event('access_denied', {'user': current_user, 'roles': required_roles})
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator 

def permission_required(permission):
    """Decorator to enforce permission-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user_roles = current_user.get('roles', ['guest'])

            if not role_manager.has_permission(user_roles, permission):
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator 

def get_user_roles_and_permissions(user_id):
    # Fetch roles and permissions from the database
    user_roles = Role.query.filter_by(user_id=user_id).all()
    user_permissions = Permission.query.filter(Permission.role_id.in_([role.id for role in user_roles])).all()
    return user_roles, user_permissions 