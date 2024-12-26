import os
import subprocess
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class SSHKeyValidator:
    """SSH Key configuration and validation"""
    
    def __init__(self, ssh_key_path: Optional[str] = None):
        self.ssh_key_path = Path(ssh_key_path or os.path.expanduser('~/.ssh/id_ed25519'))
    
    def verify_ssh_key(self) -> bool:
        """Verify SSH key exists and has correct permissions"""
        try:
            if not self.ssh_key_path.exists():
                logger.error(f"SSH key not found at {self.ssh_key_path}")
                return False
                
            # Check permissions (should be 600)
            permissions = oct(os.stat(self.ssh_key_path).st_mode)[-3:]
            if permissions != '600':
                logger.error(f"SSH key has incorrect permissions: {permissions}, should be 600")
                return False
                
            # Test GitHub SSH connection
            result = subprocess.run(
                ['ssh', '-T', 'git@github.com'],
                capture_output=True,
                text=True
            )
            
            # GitHub returns exit code 1 even for successful auth
            if "successfully authenticated" in result.stderr:
                logger.info("SSH key successfully authenticated with GitHub")
                return True
                
            logger.error(f"SSH authentication failed: {result.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"SSH key validation failed: {e}")
            return False 