from flask import current_app, Blueprint
from flask_jwt_extended import jwt_required
from flask_limiter.util import get_remote_address

bp = Blueprint('api', __name__)

@bp.route('/protected')
@jwt_required()  # Requires valid JWT token
@current_app.security_manager.limiter.limit("10 per minute")  # Custom rate limit
def protected_route():
    return {"message": "This is a protected endpoint"} 