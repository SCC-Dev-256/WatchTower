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
            for dir_path in self.directories:
                full_path = self.root_dir / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {full_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directories: {str(e)}")
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
                "requirements.txt"
            ])
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install requirements: {str(e)}")
            return False

    def setup_database(self) -> bool:
        """Initialize database"""
        try:
            # Import here to ensure dependencies are installed
            from ..database import db
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