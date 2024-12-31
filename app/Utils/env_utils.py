import os
from dotenv import load_dotenv

def load_env_file(file_path: str = '.env', override: bool = True):
    """Load environment variables from a .env file."""
    if os.path.exists(file_path):
        load_dotenv(file_path, override=override)

def get_env_variable(var_name: str, default: str = None) -> str:
    """Retrieve an environment variable with an optional default."""
    return os.getenv(var_name, default) 