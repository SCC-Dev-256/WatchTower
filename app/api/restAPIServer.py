#Deployment in a Production Environment
#Once youre ready for production youll need to deploy your Flask application:

#Web Server: Use Gunicorn or uWSGI to run Flask in production (Flask's built-in server is not suitable for production).

#Install Gunicorn: pip install gunicorn
#Run your app with Gunicorn: gunicorn api_server:app
#Reverse Proxy: Use NGINX or Apache to serve your app behind a reverse proxy. This helps with handling SSL/TLS encryption, load balancing, and static file serving.

#Cloud Providers: Deploy to cloud services like AWS, Heroku, DigitalOcean, or Google Cloud Platform.

# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, send_file, Blueprint, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_talisman import Talisman
from datetime import datetime, timedelta

import os
import secrets
from cryptography.fernet import Fernet
from pydantic import BaseModel, Field

from functools import wraps
from flask_sqlalchemy import SQLAlchemy

from app.services.encoder_manager import EncoderManager
from app.database.models.encoder import HeloEncoder

from ..core.rest_API_client import AJADevice

# import pandas as pd
# import io

from app.database import init_db, db
from flask_caching import Cache
cache = Cache()

from app.config import get_config
from app.core.monitoring.metrics import setup_metrics

from io import StringIO, BytesIO

import csv

from app.cache.redis_config import setup_cache, get_redis_client, setup_rate_limiter
from app.cache.redis_queue import EncoderQueue
from app.cache.redis_session import setup_session
from app.cache.redis_pubsub import EncoderEvents

from app.monitoring.error_tracking import ErrorTracker
from app.api.health import health_bp

from app.core.security.security_manager import SecurityManager

from app.api.routes.encoders import encoder_bp as encoder_registry
from app.api.discovery_routes import discovery_bp
from app.core.device_discovery import HeloDiscovery
import asyncio

from flask_socketio import SocketIO
from app.services.unified_websocket_service import UnifiedWebSocketService
from app.services.socketio_service import EnhancedSocketIOService
from app.services.websocket_auth import WebSocketAuthenticator

from app.models.api_key import APIKey

# Define rate limits
encoder_rate_limit = "10 per minute"  # Adjust the rate as needed

def create_app():
    app = Flask(__name__)
    
    # Initialize SocketIO services
    socketio = SocketIO()
    websocket_service = UnifiedWebSocketService(socketio)
    socketio_service = EnhancedSocketIOService()
    
    # Load config based on environment
    app.config.from_object(get_config())
    
    # Initialize Redis services
    cache = setup_cache(app)
    limiter, encoder_rate_limit = setup_rate_limiter(app)
    queue = EncoderQueue(app)
    setup_session(app)
    
    # Initialize Redis client for pub/sub
    redis_client = get_redis_client(app)
    encoder_events = EncoderEvents(redis_client)
    
    # Store services on app context
    app.encoder_queue = queue
    app.encoder_events = encoder_events
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    talisman = Talisman(app, force_https=True)
    limiter = Limiter(app, key_func=get_remote_address)
    cache.init_app(app)
    
    # Initialize database and other components
    init_db(app)
    metrics = setup_metrics(app)
    
    # Initialize cache
    cache = setup_cache(app)
    redis_client = get_redis_client(app)
    
    # Initialize error tracking
    error_tracker = ErrorTracker(app)
    
    # Register health check blueprint
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Register routes and error handlers
    register_routes(app)
    register_error_handlers(app)
    
    # Add error tracking to error handlers
    @app.errorhandler(Exception)
    def handle_error(error):
        error_tracker.track_error(error)
        return jsonify({"error": "Internal server error"}), 500
    
    # Initialize security manager
    security_manager = SecurityManager(app)
    
    # Register endpoints
    encoder_registry.register_with_flask(app)
    
    # Register discovery blueprint
    app.register_blueprint(discovery_bp, url_prefix='/discovery')
    
    # Initialize device discovery
    discovery = HeloDiscovery(encoder_registry)
    
    # Start device monitoring in background
    @app.before_first_request
    def start_monitoring():
        loop = asyncio.get_event_loop()
        loop.create_task(discovery.monitor_devices())
    
    # Initialize SocketIO and services
    socketio.init_app(app)
    websocket_service.init_app(app)
    socketio_service.init_app(app)
    
    # Register WebSocket authentication
    app.websocket_auth = WebSocketAuthenticator(app)
    
    return app

# Create the app instance
app = create_app()

#REDACTED DUE TO SUGGESTION
## Step 1: Setup Flask app and HTTPS
#app = Flask(__name__)
#db = SQLAlchemy()
#db.init_app(app)
#Talisman(app, force_https=True)  # Force HTTPS for all requests
#app.config['SESSION_COOKIE_SECURE'] = True  # Ensures cookies are only sent over HTTPS
#Talisman(app, content_security_policy={"default-src": ["'self'"]}) #Ensures external URLs are always under HTPS 
#will start running locally on http://127.0.0.1:5000.
#See document C:\Users\schum\source\repos\AJA_Log_Reporter\app\HTTPS_SSL_TLS_Certification.py

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#database table for keys, including expiration 
class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<APIKey {self.key}>"

#Does user have API KEY?
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if not api_key:
            return jsonify({"error": "No API key provided"}), 401
            
        key = api_key.split(" ")[1] if " " in api_key else api_key
        stored_api_key = APIKey.query.filter_by(key=key, is_active=True).first()
        
        if not stored_api_key or not stored_api_key.is_valid:
            return jsonify({"error": "Invalid API key"}), 401
            
        stored_api_key.update_last_used()
        return f(*args, **kwargs)
    return decorated_function


@app.route("/api/parameters/<param_id>", methods=["GET", "POST"])
@require_api_key
def get_parameter(param_id):
    # Your function implementation here
    if request.method == "GET":
        return jsonify({"message": f"Getting parameter {param_id}"})
    else:
        return jsonify({"message": f"Posting parameter {param_id}"})

#NEED TO CHECK ENV VARIABLES IF API KEY IS POSSESSED, OTHERWISE authorization check, key retreival or generate net key

#get an API key
# Step 2: Load API Key from environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

#Make sure to store your .env file securely and never commit it to version control.



def generate_api_key(user_id):
    # Generate a secure random API key
    new_api_key = secrets.token_urlsafe(32)
    
    # Save the API key to the database
    api_key = APIKey(key=new_api_key, user_id=user_id)
    db.session.add(api_key)
    db.session.commit()

    return new_api_key

#admins can create keys for users
@app.route("/generate-api-key/<user_id>", methods=["POST"])
def generate_key_for_user(user_id):
    new_api_key = generate_api_key(user_id)
    return jsonify({"api_key": new_api_key})

#Suggested to resolve 404 error
@app.route('/', endpoint='homebase')
def home():
    return "Welcome to the API! Use /api/parameters/<param_id> or /api/alarms to interact with the API."
# End Suggestion

#Adding API Key Authentification
api_key = generate_api_key(user_id=1)
print(f"Generated API Key: {api_key}")

#Json Token generation for user to hold token over software use. 
# Step 3: Setup JWT authentication
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# Example: Storing parameter values in a dictionary (simulating a database)
#C:\Users\schum\source\repos\AJA_Log_Reporter\app\Parameter_Configuration_Table.csv
parameters = {
    "eParamID_VideoInSelect": {"value": 1, "enum_values": [0, 1, 2], "description": "Video input selection"},
    "eParamID_AudioInSelect": {"value": 1, "enum_values": [0, 1, 2, 3], "description": "Audio input selection"}
}

# Route to retrieve a parameter's value
@app.route("/api/parameters/<param_id>", methods=["GET", "POST"], endpoint='parameter')
@require_api_key
def parameter(param_id):
    param = parameters.get(param_id)  # Get parameter from the dictionary
    if param:
        return jsonify(param)
    else:
        return jsonify({"error": "Parameter not found"}), 404

# Route to set a parameter's value
@app.route("/api/parameters/<param_id>", methods=["POST"])
def set_parameter(param_id):
    param = parameters.get(param_id)
    if param:
        new_value = request.json.get("value")
        if new_value in param["enum_values"]:
            param["value"] = new_value
            return jsonify({"param_id": param_id, "new_value": new_value})
        else:
            return jsonify({"error": "Invalid value"}), 400
    else:
        return jsonify({"error": "Parameter not found"}), 404

@app.route("/api/alarms", methods=["POST"], endpoint='set_alarm')
@require_api_key
def set_alarm():
    alarm_data = request.json
    alarm_type = alarm_data.get("alarm_type")
    condition = alarm_data.get("condition")
    threshold = alarm_data.get("threshold")

    # For simplicity, we'll just return the alarm data
    return jsonify({"status": "Alarm set", "alarm_type": alarm_type, "condition": condition, "threshold": threshold}), 200
    pass

# Step 4: Setup Rate Limiting
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/parameters', methods=["GET"])
@limiter.limit("5 per minute")  # Limit to 5 requests per minute
def get_parameters():
    return jsonify(message="This is the parameter data")

# Step 5: Input Validation using Pydantic
class ParameterSchema(BaseModel):
    value: int = Field(..., gt=0, lt=10)  # Only allow values between 1 and 10
    description: str

# Step 6: Define Routes
@app.route('/login', methods=['POST'])
def login():
    access_token = create_access_token(identity="user_id", additional_claims={"role": "admin"})
    return jsonify(access_token=access_token)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(message=f"Welcome, {current_user}!")

@app.route('/set-parameter', methods=['POST'])
def set_parameter():
    data = request.json
    try:
        parameter = ParameterSchema(**data)  # Validate the data
        return jsonify(parameter.dict())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify(message="Forbidden"), 403
    return jsonify(message="Admin access granted")

# Initialize encoder manager
encoder_manager = EncoderManager(db)

@app.route("/api/encoders", methods=["GET"])
@require_api_key
@cache.cached(timeout=300, key_prefix='list_encoders')  # Cache for 5 minutes
def list_encoders():
    encoders = HeloEncoder.query.all()
    return jsonify([{
        "id": e.id,
        "name": e.name,
        "ip_address": e.ip_address,
        "status": e.status,
        "streaming": e.streaming_state,
        "recording": e.recording_state,
        "last_checked": e.last_checked.isoformat()
    } for e in encoders])

@app.route("/api/encoders/<int:encoder_id>/control", methods=["POST"])
@require_api_key
@limiter.limit(encoder_rate_limit)  # Custom rate limit
def control_encoder(encoder_id):
    """Control encoder streaming/recording"""
    encoder = HeloEncoder.query.get_or_404(encoder_id)
    action = request.json.get("action")
    
    try:
        device = AJADevice(f"http://{encoder.ip_address}")
        
        if action == "start_streaming":
            device.set_param("eParamID_ReplicatorCommand", 3)
        elif action == "stop_streaming":
            device.set_param("eParamID_ReplicatorCommand", 4)
        return jsonify({"status": "success", "action": action})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/encoders/status", methods=["GET"])
@require_api_key
@cache.cached(timeout=60, key_prefix='encoder_status')
def get_encoder_status():
    """Get status summary of all encoders"""
    encoders = HeloEncoder.query.all()
    
    # Update Prometheus metrics
    current_app.update_encoder_metrics(encoders)
    
    summary = {
        "total": len(encoders),
        "online": sum(1 for e in encoders if e.status == "online"),
        "streaming": sum(1 for e in encoders if e.streaming_state),
        "recording": sum(1 for e in encoders if e.recording_state),
        "offline": sum(1 for e in encoders if e.status == "offline"),
        "not_checked": sum(1 for e in encoders if e.last_checked < datetime.utcnow() - timedelta(minutes=5))
    }
    
    return jsonify(summary)

@app.route("/api/alerts/history", methods=["GET"])
@require_api_key
def get_alert_history():
    """Get alert history with optional filtering"""
    encoder_name = request.args.get('encoder_name')
    severity = request.args.get('severity')
    status = request.args.get('status', 'active')
    
    alerts = current_app.error_tracker.alert_history.get_active_alerts()
    
    # Apply filters
    if encoder_name:
        alerts = [a for a in alerts if a['encoder_name'] == encoder_name]
    if severity:
        alerts = [a for a in alerts if a['severity'] == severity]
    if status:
        alerts = [a for a in alerts if a['status'] == status]
        
    return jsonify(alerts)

if __name__ == "__main__":
    app.run(debug=True)

import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@app.errorhandler(404)
def not_found(error):
    logging.error(f"Error 404: {error}")
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Error 500: {error}")
    return jsonify({"error": "Internal server error"}), 500

def register_routes(app):
    """Register all application routes"""
    # Register blueprints
    from .routes.encoders import encoder_bp
    from .routes.monitoring import monitoring_bp
    
    app.register_blueprint(encoder_bp)
    app.register_blueprint(monitoring_bp)

def register_error_handlers(app):
    """Register application error handlers"""
    from app.core.error_handling.handlers import ErrorHandler
    
    # Initialize central error handler
    error_handler = ErrorHandler(app)
    app.error_handler = error_handler  # Make available app-wide
    
    # Register handlers for different error types
    app.register_error_handler(Exception, error_handler.handle_error)
    app.register_error_handler(404, lambda e: error_handler.handle_error(e, {'type': 'not_found'}))
    app.register_error_handler(500, lambda e: error_handler.handle_error(e, {'type': 'server_error'}))