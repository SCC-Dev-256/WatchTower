from flask_caching import Cache
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def setup_cache(app):
    cache = Cache(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': app.config['REDIS_URL']
    })
    return cache

def get_redis_client(app):
    return Redis.from_url(app.config['REDIS_URL'])

def setup_rate_limiter(app):
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        storage_uri=app.config['REDIS_URL'],
        default_limits=["200 per day", "50 per hour"]
    )
    
    def encoder_rate_limit():
        return "30 per minute"
        
    return limiter, encoder_rate_limit
