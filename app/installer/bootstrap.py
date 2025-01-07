import json
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List
import requests
import yaml

class Bootstrapper:
    def __init__(self, config_url: str = "https://your-domain.com/installer-config.yml"):
        self.config_url = config_url
        self.logger = self._setup_logging()
        self.root_dir = Path(__file__).parent.parent.parent
        self.requirements_dir = self.root_dir / 'requirements'
        self.requirements = []
        self.directories = []
        self.config = {}

    def _setup_logging(self) -> logging.Logger:
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('installer.log')
            ]
        )
        return logging.getLogger('installer')

    def fetch_config(self) -> bool:
        """Fetch configuration from remote source"""
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
            return False

    def create_directories(self) -> bool:
        """Create required directory structure"""
        try:
            # Create requirements directory
            self.requirements_dir.mkdir(parents=True, exist_ok=True)
            
            # Create other directories from config
            for dir_path in self.directories:
                full_path = self.root_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {full_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directories: {str(e)}")
            return False

    def setup_requirements(self) -> bool:
        """Setup and compile requirements files"""
        try:
            # Install pip-tools first
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                "pip-tools"
            ])

            # Create base requirements.in
            base_reqs = """# Core dependencies
Flask==2.3.3
Flask-CORS>=4.0.0
requests==2.26.0
aiohttp>=3.8.0
python-json-logger>=2.0.0
PyYAML>=6.0.1
SQLAlchemy==2.0.36
flask-jwt-extended==4.5.3
Flask-Limiter[redis]==3.5.0
python-dotenv>=1.0.0
cryptography>=41.0.0
pydantic==2.4.2
Flask-Pydantic>=0.11.0,<0.12.0
flask-openapi3==3.0.1
Flask-Caching==2.1.0
redis==5.0.1
Flask-SQLAlchemy==3.1.1
python-telegram-bot>=20.7
gunicorn==21.2.0
flask-talisman>=1.1.0
psutil==5.9.5
flask-socketio==5.3.6
rq==1.15.1
Flask-Session==0.5.0"""

            reqs_in = self.requirements_dir / 'requirements.in'
            reqs_in.write_text(base_reqs)

            # Compile requirements
            subprocess.run([
                'pip-compile',
                str(reqs_in),
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

    def setup_database(self) -> bool:
        """Initialize database"""
        try:
            # Import here to ensure dependencies are installed
            from app.core.database import db
            from flask import Flask
            
            app = Flask(__name__)
            app.config['SQLALCHEMY_DATABASE_URI'] = self.config.get('database_url', 
                'postgresql://localhost/encoder_manager')
            
            with app.app_context():
                db.create_all()
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup database: {str(e)}")
            return False

    def run(self) -> bool:
        """Run the complete installation process"""
        steps = [
            (self.fetch_config, "Fetching configuration"),
            (self.create_directories, "Creating directories"),
            (self.setup_requirements, "Setting up requirements"),
            (self.install_requirements, "Installing requirements"),
            (self.setup_database, "Setting up database")
        ]

        for step_func, step_name in steps:
            self.logger.info(f"Starting: {step_name}")
            if not step_func():
                self.logger.error(f"Failed: {step_name}")
                return False
            self.logger.info(f"Completed: {step_name}")

        return True

if __name__ == "__main__":
    bootstrapper = Bootstrapper()
    success = bootstrapper.run()
    sys.exit(0 if success else 1)