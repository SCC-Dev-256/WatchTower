from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_caching import Cache
from flask_session import Session
from flask_talisman import Talisman
from flask_pydantic import validate

# Initialize Flask extensions
db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()
limiter = Limiter(key_func=lambda: "global")
cache = Cache()
session = Session()
talisman = Talisman()

def create_app(config_object='app.config.config.Settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    session.init_app(app)
    talisman.init_app(app)

    # Register blueprints
    from .api.routes import encoder_bp, monitoring_bp
    app.register_blueprint(encoder_bp)
    app.register_blueprint(monitoring_bp)

    return app

__all__ = [
    'create_app',
    'db',
    'socketio',
    'jwt',
    'limiter',
    'cache',
    'session',
    'talisman'
] 