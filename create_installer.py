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
]) 