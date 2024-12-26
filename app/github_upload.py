import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)

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