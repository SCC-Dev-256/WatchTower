import PyInstaller.__main__
import sys

PyInstaller.__main__.run([
    'app/installer/bootstrap.py',
    '--onefile',
    '--name=encoder_manager_setup',
    '--add-data=installer-config.yml:.',
    '--hidden-import=yaml',
    '--hidden-import=sqlalchemy',
    '--hidden-import=flask_sqlalchemy',
    '--hidden-import=flask',
    '--hidden-import=flask_socketio',
    '--hidden-import=redis',
    '--hidden-import=psycopg2',
    '--hidden-import=alembic',
    '--hidden-import=pydantic',
    '--hidden-import=flask_limiter',
    '--hidden-import=flask_caching',
    '--hidden-import=python_telegram_bot',
]) 