from functools import wraps
from flask import current_app, request
from flask_socketio import disconnect
import jwt
from datetime import datetime, timedelta
import hashlib
import hmac
import json
from app.core.error_handling.decorators import handle_errors

class WebSocketSecurity:
    # This class is still used but should be imported from unified service
    ...