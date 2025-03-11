import json, os, sys, subprocess, logging, requests, yaml, sqlalchemy, pathlib, typing
from pathlib import Path
from typing import Dict, List
from sqlalchemy import create_engine
from logging.handlers import RotatingFileHandler

class Bootstrapper:
    def __init__(self, config_url: str = None):
        self.config_url = config_url or os.getenv('CONFIG_URL', 'https://your-domain.com/installer-config.yml')
        self.logger = self._setup_logging()
        self.root_dir = Path(__file__).parent.parent.parent
        self.requirements_dir = self.root_dir / 'requirements/files'
        self.requirements = []
        self.directories = []
        self.config = {}

    def _setup_logging(self) -> logging.Logger:
        """Configure logging with rotation"""
        handler = RotatingFileHandler('installer.log', maxBytes=5*1024*1024, backupCount=3)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                handler
            ]
        )
        return logging.getLogger('installer')

    def fetch_config(self) -> bool:
        """Fetch configuration from remote source or local fallback"""
        try:
            response = requests.get(self.config_url)
            response.raise_for_status()
            self.config = yaml.safe_load(response.text)
            self.requirements = self.config.get('requirements', [])
            self.directories = self.config.get('directories', [])
            return True
        except Exception as e:
            self.logger.error(f"Failed to fetch config: {str(e)}")
            # Fall back to local config if available
            local_config = Path('installer-config.yml')
            if local_config.exists():
                self.config = yaml.safe_load(local_config.read_text())
                return True
            else:
                self.logger.warning("No local config found, using default configuration.")
                self.config = {
                    'database_url': os.getenv('DATABASE_URL', 'postgresql://localhost/encoder_manager'),
                    'requirements': [],
                    'directories': []
                }
                return True

    def validate_directories(self) -> bool:
        """Validate the required directory structure"""
        try:
            # Check if requirements directory exists
            if not self.requirements_dir.exists():
                self.logger.error(f"Missing directory: {self.requirements_dir}")
                return False
            # Check other directories from config
            for dir_path in self.directories:
                full_path = self.root_dir / dir_path
                if not full_path.exists():
                    self.logger.error(f"Missing directory: {full_path}")
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Error validating directories: {str(e)}")
            return False

    def create_directories(self) -> bool:
        """Create required directory structure with error handling"""
        try:
            # Create requirements directory
            self.requirements_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {self.requirements_dir}")
            # Create other directories from config
            for dir_path in self.directories:
                full_path = self.root_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {full_path}")
            return True
        except FileExistsError as e:
            self.logger.warning(f"Directory already exists: {str(e)}")
            return True
        except PermissionError as e:
            self.logger.error(f"Permission denied: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to create directories: {str(e)}")
            return False

    def setup_requirements(self) -> bool:
        """Setup and compile requirements files with custom dependency sets"""
        try:
            # Install pip-tools first
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "pip-tools"
            ])

            # Compile requirements
            subprocess.run([
                'pip-compile',
                str(self.requirements_dir / 'requirements.in'),
                f'--output-file={str(self.requirements_dir)}/requirements.txt'
            ], check=True)

            return True
        except Exception as e:
            self.logger.error(f"Failed to setup requirements: {str(e)}")
            return False

    def install_requirements(self) -> bool:
        """Install Python dependencies"""
        try:
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(self.requirements_dir / "requirements.txt")
            ])
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install requirements: {str(e)}")
            return False

    def validate_database_connection(self) -> bool:
        """Validate the database connection"""
        try:
            engine = create_engine(self.config.get('database_url', 'postgresql://localhost/encoder_manager'))
            connection = engine.connect()
            connection.close()
            self.logger.info("Database connection validated successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Database connection validation failed: {str(e)}")
            return False

    def setup_database(self) -> bool:
        """Initialize database with Alembic migrations"""
        try:
            if not self.validate_database_connection():
                return False
            # Run Alembic migrations
            subprocess.run([
                'alembic',
                'upgrade',
                'head'
            ], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup database: {str(e)}")
            return False

    def run(self) -> bool:
        """Run the complete installation process with directory validation"""
        if not self.validate_directories():
            self.logger.error("Directory validation failed.")
            print("Error: Directory validation failed. Please check the logs for more details.")
            return False
        steps = [
            (self.fetch_config, "Fetching configuration"),
            (self.create_directories, "Creating directories"),
            (self.setup_requirements, "Setting up requirements"),
            (self.install_requirements, "Installing requirements"),
            (self.setup_database, "Setting up database")
        ]

        for step_func, step_name in steps:
            self.logger.info(f"Starting: {step_name}")
            print(f"Starting: {step_name}")
            if not step_func():
                self.logger.error(f"Failed: {step_name}")
                print(f"Error: {step_name} failed. Please check the logs for more details.")
                return False
            self.logger.info(f"Completed: {step_name}")
            print(f"Completed: {step_name}")

        print("Setup completed successfully.")
        return True

if __name__ == "__main__":
    bootstrapper = Bootstrapper()
    success = bootstrapper.run()
    sys.exit(0 if success else 1)