import logging
import subprocess
import os
import time
from typing import Optional
import requests
#Not Functional due to the import of the ssh_validator causing the app to check for app.core.database, which doesn't exist and then fails. 
#from app.core.config.ssh_validator import SSHKeyValidator

import sys
from unittest.mock import MagicMock

sys.modules['app.core.database'] = MagicMock()


logger = logging.getLogger(__name__)

class GitHubUploader:
    """Enhanced GitHub repository management"""

    def __init__(self, config):
        self.config = config
        #self.ssh_validator = SSHKeyValidator(
        #    ssh_key_path=os.getenv('SSH_KEY_PATH')
        #)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
        )

    def create_and_push(self) -> bool:
        """Create repository and push code"""
        try:
            # Verify SSH key before attempting push
            #if not self.ssh_validator.verify_ssh_key():
            #    logger.error("SSH key validation failed")
            #    return False

            if self.create_repo() and self.push_code():
                logger.info("Repository setup completed successfully!")
                return True
            return False
        except Exception as e:
            logger.error(f"Repository setup failed: {e}")
            return False

    def create_repo(self) -> bool:
        """Create GitHub repository with retry logic"""
        for attempt in range(self.config.api.max_retries):
            try:
                response = requests.post(
                    f"{self.config.api.base_url}/user/repos",
                    headers=self.config.get_auth_headers(),
                    json={
                        "name": self.config.github.repo_name,
                        "private": self.config.github.is_private
                    },
                    timeout=self.config.api.timeout
                )
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                if response.status_code == 422:  # Repository exists
                    return True
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.api.max_retries - 1:
                    time.sleep(self.config.api.retry_delay)
        return False

    def push_code(self) -> bool:
        """Push code to GitHub using SSH authentication"""
        try:
            os.chdir(self.config.github.local_path)

            # Windows-specific: Use absolute path for SSH key
            ssh_key_path = os.path.expanduser(os.getenv('SSH_KEY_PATH', '~/.ssh/id_ed25519'))
            os.environ['GIT_SSH_COMMAND'] = f'ssh -i "{ssh_key_path}"'

            self._run_git_command(['git', 'init'])
            self._run_git_command(['git', 'add', '.'])
            self._run_git_command(['git', 'commit', '-m', os.getenv('GIT_COMMIT_MESSAGE', 'Initial commit')])

            # Ensure remote doesn't already exist
            try:
                self._run_git_command(['git', 'remote', 'remove', 'origin'])
            except:
                pass

            remote_url = f"git@github.com:{self.config.github.username}/{self.config.github.repo_name}.git"
            self._run_git_command(['git', 'remote', 'add', 'origin', remote_url])
            self._run_git_command(['git', 'branch', '-M', self.config.github.default_branch])
            self._run_git_command(['git', 'push', '-u', 'origin', self.config.github.default_branch])

            return True
        except Exception as e:
            logger.error(f"Failed to push code: {e}")
            return False

    def _run_git_command(self, command: list) -> Optional[str]:
        """Execute git command with error handling"""
        try:
            logger.debug(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Command output: {result.stdout}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise

if __name__ == "__main__":
    # Assuming config is passed or loaded here
    config = ...  # Load or pass the configuration
    uploader = GitHubUploader(config)
    uploader.create_and_push()
