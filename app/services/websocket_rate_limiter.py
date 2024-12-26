from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class WebSocketRateLimiter:
    def __init__(self, rate_limit=100, time_window=60):
        self.rate_limit = rate_limit  # messages per time window
        self.time_window = time_window  # seconds
        self.client_messages = defaultdict(list)
        
    def check_rate_limit(self, client_id: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Clean old messages
        self.client_messages[client_id] = [
            timestamp for timestamp in self.client_messages[client_id]
            if timestamp > window_start
        ]
        
        # Check rate limit
        if len(self.client_messages[client_id]) >= self.rate_limit:
            return False
            
        # Add new message timestamp
        self.client_messages[client_id].append(now)
        return True 