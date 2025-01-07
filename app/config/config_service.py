import os

class ConfigService:
    def get_config(self, key, default=None):
        return os.getenv(key, default) 