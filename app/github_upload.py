import logging
import subprocess
import os
import time
from typing import Optional
import requests
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env file and allow it to override system env variables
if os.path.exists('.env'):
    load_dotenv('.env', override=True)

# Retrieve GITHUB_TOKEN
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN:
    print(f"Using GITHUB_TOKEN from .env: {GITHUB_TOKEN[:15]}...{GITHUB_TOKEN[-4:]}")
else:
    print("GITHUB_TOKEN not found in any source.")

# Check all possible environment sources
env_sources = {
    '.env file': os.path.exists('.env'),
    'Environment': bool(os.environ.get('GITHUB_TOKEN')),
    'Docker env': os.path.exists('/.dockerenv'),
    'System env': bool(subprocess.run('printenv GITHUB_TOKEN', shell=True, capture_output=True).stdout)
}

print("\nPossible token sources:")
for source, exists in env_sources.items():
    print(f"{source}: {'Present' if exists else 'Not found'}")

# Confirm the active token source
if os.getenv("GITHUB_TOKEN"):
    print("\nUsing token from environment (overrides .env).")
else:
    print("\nUsing token from .env file.")

logger = logging.getLogger(__name__)

class GitHubConfig(BaseModel):
    username: str
    token: str
    repo_name: str
    local_path: Path
    is_private: bool = False
    default_branch: str = "main"

class APIConfig(BaseModel):
    base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5

class GitHubUploader:
    """Enhanced GitHub repository management"""

    def __init__(self, github_config: GitHubConfig, api_config: APIConfig):
        self.github_config = github_config
        self.api_config = api_config
        self._setup_logging()
        self._log_environment()

    def _setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=os.getenv('LOG_LEVEL', 'DEBUG'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
        )

    def _log_environment(self):
        """Log environment variables"""
        logger.debug("Environment Variables:")
        logger.debug(f"GITHUB_USERNAME: {os.getenv('GITHUB_USERNAME')}")
        logger.debug(f"GITHUB_TOKEN: {os.getenv('GITHUB_TOKEN')}")
        logger.debug(f"REPO_NAME: {os.getenv('REPO_NAME')}")
        logger.debug(f"LOCAL_REPO_PATH: {os.getenv('LOCAL_REPO_PATH')}")
        logger.debug(f"SSH_KEY_PATH: {os.getenv('SSH_KEY_PATH')}")

    def create_and_push(self) -> bool:
        """Create repository and push code"""
        logger.debug("Starting create_and_push process")
        try:
            if self.create_repo() and self.push_code():
                logger.info("Repository setup completed successfully!")
                return True
            return False
        except Exception as e:
            logger.error(f"Repository setup failed: {e}", exc_info=True)
            return False
        finally:
            logger.debug("Finished create_and_push process")

    def create_repo(self) -> bool:
        """Create GitHub repository with retry logic"""
        logger.debug("Starting create_repo process")
        for attempt in range(self.api_config.max_retries):
            try:
                response = requests.post(
                    f"{self.api_config.base_url}/user/repos",
                    headers={
                        "Authorization": f"Bearer {self.github_config.token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={
                        "name": self.github_config.repo_name,
                        "private": self.github_config.is_private
                    },
                    timeout=self.api_config.timeout
                )
                logger.debug(f"GitHub API response: {response.status_code} - {response.text}")
                response.raise_for_status()
                return True
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed during repository creation: {e}. Repo: {self.github_config.repo_name}, User: {self.github_config.username}", exc_info=True)
                if response.status_code == 422:  # Repository exists
                    logger.info("Repository already exists, proceeding with push.")
                    return True
                if attempt < self.api_config.max_retries - 1:
                    logger.info(f"Retrying in {self.api_config.retry_delay} seconds...")
                    time.sleep(self.api_config.retry_delay)
        logger.error("Failed to create repository after multiple attempts.")
        return False

    def push_code(self) -> bool:
        """Push code to GitHub using SSH authentication"""
        logger.debug("Starting push_code process")
        try:
            os.chdir(self.github_config.local_path)
            ssh_key_path = os.path.expanduser(os.getenv('SSH_KEY_PATH', '~/.ssh/id_ed25519'))
            os.environ['GIT_SSH_COMMAND'] = f'ssh -i "{ssh_key_path}"'
           

            self._run_git_command(['git', 'init'])
            self._run_git_command(['git', 'add', '.'])

            # Prompt the user for a commit message
            commit_message = input("Enter a commit message: ")
            self._run_git_command(['git', 'commit', '-m', commit_message])
            try:
                self._run_git_command(['git', 'remote', 'remove', 'origin'])
            except subprocess.CalledProcessError:
                pass

            remote_url = f"git@github.com:{self.github_config.username}/{self.github_config.repo_name}.git"
            self._run_git_command(['git', 'remote', 'add', 'origin', remote_url])
            self._run_git_command(['git', 'branch', '-M', self.github_config.default_branch])
            self._run_git_command(['git', 'push', '-u', 'origin', self.github_config.default_branch])

            return True
        except Exception as e:
            logger.error(f"Failed to push code. Please check your network connection and SSH key configuration: {e}", exc_info=True)
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
            logger.error(f"Git command failed: {e.stderr}", exc_info=True)
            raise

if __name__ == "__main__":
    # Initialize configuration
    github_config = GitHubConfig(
        username=os.getenv('GITHUB_USERNAME'),
        token=os.getenv('GITHUB_TOKEN'),
        repo_name=os.getenv('REPO_NAME'),
        local_path=Path(os.getenv('LOCAL_REPO_PATH')),
        is_private=os.getenv('REPO_PRIVATE', 'false').lower() == 'true',
        default_branch=os.getenv('DEFAULT_BRANCH', 'main')
    )
    api_config = APIConfig(
        base_url=os.getenv('API_BASE_URL', 'https://api.github.com/user/repos'),
        timeout=int(os.getenv('API_TIMEOUT', 30)),
        max_retries=int(os.getenv('API_MAX_RETRIES', 3)),
        retry_delay=int(os.getenv('API_RETRY_DELAY', 5))
    )

    uploader = GitHubUploader(github_config, api_config)
    uploader.create_and_push()
    # Verify environment variables
    print("GITHUB_USERNAME:", os.getenv('GITHUB_USERNAME'))
    print(f"Using GITHUB_TOKEN: {GITHUB_TOKEN[:15]}...{GITHUB_TOKEN[-4:]}")
    print("REPO_NAME:", os.getenv('REPO_NAME'))

    logger.debug(f"Using GitHub token: {os.getenv('GITHUB_TOKEN')}")

