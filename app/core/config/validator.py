from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import os
import re
from dotenv import load_dotenv
import logging
from base64 import b64encode
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class GitHubConfig:
    """GitHub configuration settings"""
    username: str
    token: str
    repo_name: str
    local_path: Path
    is_private: bool = False
    default_branch: str = "main"
    
    def validate(self) -> None:
        """Validate GitHub configuration"""
        if not re.match(r'^[a-zA-Z0-9-]+$', self.repo_name):
            raise ValueError("Repository name contains invalid characters")
        if not self.local_path.exists():
            raise ValueError(f"Local path does not exist: {self.local_path}")

@dataclass
class APIConfig:
    """API configuration settings"""
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    token_expiry_days: int = 30
    encryption_key: Optional[bytes] = None
    
    def __post_init__(self):
        """Initialize encryption key if not provided"""
        if not self.encryption_key:
            self.encryption_key = Fernet.generate_key()

class ConfigValidator:
    """Configuration validation and management"""
    
    def __init__(self):
        load_dotenv()
        self.github = self._load_github_config()
        self.api = self._load_api_config()
        self.security = self._load_security_config()
        self._fernet = Fernet(self.security.encryption_key)
        
    def _load_github_config(self) -> GitHubConfig:
        """Load and validate GitHub configuration"""
        config = GitHubConfig(
            username=os.getenv('GITHUB_USERNAME', ''),
            token=os.getenv('GITHUB_TOKEN', ''),
            repo_name=os.getenv('REPO_NAME', 'WatchTower'),
            local_path=Path(os.getenv('LOCAL_REPO_PATH', '')),
            is_private=os.getenv('REPO_PRIVATE', 'false').lower() == 'true',
            default_branch=os.getenv('DEFAULT_BRANCH', 'main')
        )
        config.validate()
        return config
    
    def _load_api_config(self) -> APIConfig:
        """Load API configuration"""
        return APIConfig(
            base_url=os.getenv('API_BASE_URL', 'https://api.github.com'),
            timeout=int(os.getenv('API_TIMEOUT', '30')),
            max_retries=int(os.getenv('API_MAX_RETRIES', '3')),
            retry_delay=int(os.getenv('API_RETRY_DELAY', '5'))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            token_expiry_days=int(os.getenv('API_KEY_EXPIRY_DAYS', '30')),
            encryption_key=os.getenv('ENCRYPTION_KEY', '').encode()
        )
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt sensitive token"""
        return self._fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt sensitive token"""
        return self._fernet.decrypt(encrypted_token.encode()).decode()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authenticated headers with encrypted token"""
        return {
            "Authorization": f"token {self.github.token}",
            "Accept": "application/vnd.github.v3+json"
        } 