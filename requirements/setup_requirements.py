# setup_requirements.py
import os
import subprocess
from pathlib import Path


def validate_requirements_directory() -> bool:
    """Validate the existence of the requirements directory"""
    try:
        requirements_dir = Path('requirements/files')
        if not requirements_dir.exists():
            print(f"Missing directory: {requirements_dir}")
            return False
        return True
    except Exception as e:
        print(f"Error validating requirements directory: {str(e)}")
        return False

def create_requirements_files():
    # Create requirements directory if it doesn't exist
    requirements_dir = Path('requirements/files')
    requirements_dir.mkdir(parents=True, exist_ok=True)
    
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
redis==5.0.1
rq==1.15.1
Flask-Session==0.5.0
Flask-SocketIO==5.3.6

# Monitoring
psutil==5.9.5
structlog==23.1.0

# Additional dependencies
requests==2.31.0
sqlalchemy==2.0.21
google-api-python-client==2.92.0
google-auth==2.23.0
icalendar==5.0.7
pdfplumber==0.9.0
feedparser==6.0.10
beautifulsoup4==4.12.2
torch==2.0.1
numpy==1.25.2
soundfile==0.12.1
librosa==0.10.0
faster-whisper==0.1.0
whisper-timestamped==0.1.0
mlx-whisper==0.1.0
diart==0.1.0
rx==3.2.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.11.0
"""

    # Write base requirements
    (requirements_dir / 'requirements.in').write_text(base_content)

def compile_requirements():
    # Ensure pip-tools is installed
    subprocess.run(['pip', 'install', 'pip-tools'], check=True)
    
    # Compile requirements
    subprocess.run([
        'pip-compile',
        'requirements/files/requirements.in',
        '--output-file=requirements/files/requirements.txt'
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
    print("pip-sync requirements/files/requirements.txt  # for all environments")

if __name__ == '__main__':
    main()