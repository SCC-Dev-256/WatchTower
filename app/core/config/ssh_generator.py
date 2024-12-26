import os
import subprocess
from pathlib import Path
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class SSHKeyGenerator:
    """Generate and configure SSH keys for GitHub authentication"""
    
    def __init__(self, email: str, key_path: Optional[str] = None):
        self.email = email
        self.key_path = Path(key_path or os.path.expanduser('~/.ssh/id_ed25519'))
        
    def generate_key(self) -> Tuple[bool, str]:
        """Generate new SSH key pair"""
        try:
            if self.key_path.exists():
                return False, f"SSH key already exists at {self.key_path}"
                
            # Create .ssh directory if it doesn't exist
            self.key_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            
            # Generate key
            subprocess.run([
                'ssh-keygen',
                '-t', 'ed25519',
                '-C', self.email,
                '-f', str(self.key_path),
                '-N', ''  # Empty passphrase
            ], check=True)
            
            # Set correct permissions
            os.chmod(self.key_path, 0o600)
            os.chmod(f"{self.key_path}.pub", 0o644)
            
            # Get public key content
            with open(f"{self.key_path}.pub") as f:
                public_key = f.read().strip()
                
            return True, public_key
            
        except Exception as e:
            return False, f"Failed to generate SSH key: {e}"
    
    def add_to_agent(self) -> Tuple[bool, str]:
        """Add key to SSH agent"""
        try:
            subprocess.run(['ssh-agent', '-s'], check=True)
            subprocess.run(['ssh-add', str(self.key_path)], check=True)
            return True, "Key added to SSH agent"
        except Exception as e:
            return False, f"Failed to add key to SSH agent: {e}" 