# setup_requirements.py
import os
import subprocess
from pathlib import Path


def validate_requirements_directory() -> bool:
    """Validate the existence of the requirements directory"""
    try:
        requirements_dir = Path('requirements')
        if not requirements_dir.exists():
            print(f"Missing directory: {requirements_dir}")
            return False
        return True
    except Exception as e:
        print(f"Error validating requirements directory: {str(e)}")
        return False

def create_requirements_files():
    # Create requirements directory if it doesn't exist
    requirements_dir = Path('requirements')
    requirements_dir.mkdir(exist_ok=True)
    
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
"""

    # Custom dependency sets
    development = [
        "black==23.12.1",
        "flake8==7.0.0",
        "ipython==8.15.0",
        "pip-tools==6.11.0"
    ]
    testing = [
        "pytest==7.4.3",
        "pytest-cov==4.1.0",
        "pytest-mock==3.11.0"
    ]
    production = [
        "gunicorn==21.2.0",
        "psycopg2-binary==2.9.9"  # For Linux
    ]

    # Write base requirements
    (requirements_dir / 'requirements.in').write_text(base_content)

    # Write custom dependency sets
    (requirements_dir / 'development.in').write_text("\n".join(development))
    (requirements_dir / 'testing.in').write_text("\n".join(testing))
    (requirements_dir / 'production.in').write_text("\n".join(production))

def compile_requirements():
    # Ensure pip-tools is installed
    subprocess.run(['pip', 'install', 'pip-tools'], check=True)
    
    # Compile requirements
    subprocess.run([
        'pip-compile',
        'requirements/requirements.in',
        '--output-file=requirements/requirements.txt'
    ], check=True)

def main():
    print("Setting up requirements files...")
    if not validate_requirements_directory():
        print("Requirements directory validation failed.")
        return
    create_requirements_files()
    print("Compiling requirements...")
    compile_requirements()
    print("\nRequirements setup complete!")
    print("You can now use:")
    print("pip-sync requirements/requirements.txt  # for all environments")
    print("pip-sync requirements/development.txt  # for development")
    print("pip-sync requirements/testing.txt  # for testing")
    print("pip-sync requirements/production.txt  # for production")

if __name__ == '__main__':
    main()