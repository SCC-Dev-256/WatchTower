from flask_session import Session
from datetime import timedelta
from redis import Redis

def setup_session(app):
    app.config.update(
        SESSION_TYPE='redis',
        SESSION_REDIS=Redis.from_url(app.config['REDIS_URL']),
        PERMANENT_SESSION_LIFETIME=timedelta(days=1)
    )
    Session(app)
    return app 