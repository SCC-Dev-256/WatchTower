from functools import wraps
from flask import request
from app.core.error_handling.errors import ValidationError, handle_api_error
from app.core.auditing_log import LoggingSystem
 
def validate_request(schema_class):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                
                validated_data = schema_class(**data)
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except Exception as e:
                raise ValidationError(str(e), details=getattr(e, 'errors', lambda: {})())
                
        return decorated_function
    return decorator 