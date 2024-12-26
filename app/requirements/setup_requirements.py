# setup_requirements.py
import os
import subprocess
from pathlib import Path

def create_requirements_files():
    # Create requirements directory
    Path('requirements').mkdir(exist_ok=True)
    
    # Base requirements
    base_content = """# Web Framework
Flask==2.3.3
flask-talisman==1.1.0
datetime==5.1.0
requests==2.26.0
gunicorn==21.2.0

# Database
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Security & Auth
flask-jwt-extended==4.5.3
Flask-Limiter==3.5.0
python-dotenv>=1.0.0
cryptography>=41.0.0

# Validation & API Docs
pydantic>=2.5.0
flask-openapi3==3.0.1

# Caching
Flask-Caching==2.1.0
redis==5.0.1

# Monitoring
prometheus-flask-exporter==0.22.4
"""

    # Dev requirements
    dev_content = """-r base.in

# Development Tools
black==23.10.1
flake8==6.1.0
ipython==8.15.0
pip-tools==6.11.0
"""

    # Test requirements
    test_content = """-r base.in

# Testing
pytest==7.4.3
pytest-cov==4.1.0
    pytest-mock==3.11.0
"""

    # Write files
    Path('requirements/base.in').write_text(base_content)
    Path('requirements/dev.in').write_text(dev_content)
    Path('requirements/test.in').write_text(test_content)

def compile_requirements():
    # Install pip-tools
    subprocess.run(['pip', 'install', 'pip-tools'], check=True)
    
    # Compile requirements
    for req_type in ['base', 'dev', 'test']:
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
    print("pip-sync requirements/dev.txt   # for development")
    print("pip-sync requirements/test.txt  # for testing")

if __name__ == '__main__':
    main()