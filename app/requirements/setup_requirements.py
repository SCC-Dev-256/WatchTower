# setup_requirements.py
import os
import subprocess
from pathlib import Path

def create_requirements_files():
    # Create requirements directory if it doesn't exist
    Path('requirements').mkdir(exist_ok=True)
    
    # Base requirements content
    base_content = """# Core dependencies
Flask==2.3.3
flask-sqlalchemy==3.1.1
flask-migrate==4.0.5
flask-jwt-extended==4.5.3
Flask-Limiter==3.5.0
pydantic==2.4.2
flask-openapi3==3.0.1
Flask-Caching==2.1.0
prometheus-flask-exporter==0.22.4
python-dotenv>=1.0.0

# Redis Integration
redis==5.0.1
rq==1.15.1
Flask-Session==0.5.0
Flask-SocketIO==5.3.6

# Monitoring
psutil==5.9.5
structlog==23.1.0

# Development Tools
black==23.12.1
flake8==7.0.0
ipython==8.15.0
pip-tools==6.11.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.11.0

# Production-specific requirements
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For Linux
"""

    # Write files
    Path('requirements').write_text(base_content)

def compile_requirements():
    # Ensure pip-tools is installed
    subprocess.run(['pip', 'install', 'pip-tools'], check=True)
    
    # Compile requirements
    for req_type in ['base', 'dev', 'prod']:
        subprocess.run([
            'pip-compile',
            f'requirements/{req_type}.in',
            f'--output-file=requirements/{req_type}.txt'
        ], check=True)

def main():
    print("Setting up requirements files...")
    create_requirements_files()
    print("Compiling requirements...")
    compile_requirements()
    print("\nRequirements setup complete!")
    print("You can now use:")
    print("pip-sync requirements/base.txt  # for production")


if __name__ == '__main__':
    main()