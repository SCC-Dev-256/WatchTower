from .encoder_operations import encoder_ops_bp
from functools import wraps
from flask import request, abort

def api_version(min_version):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            version = request.headers.get('API-Version', '1.0')
            if float(version) < min_version:
                abort(400, f'API version {min_version} or higher required')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage example:
@encoder_ops_bp.route('/encoders/advanced-config', methods=['POST'])
@api_version(1.1)  # Requires API version 1.1 or higher
def advanced_config():
    pass 