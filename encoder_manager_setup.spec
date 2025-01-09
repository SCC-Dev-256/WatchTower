# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\installer\\bootstrap.py'],
    pathex=[],
    binaries=[],
    datas=[('installer-config.yml', '.')],
    hiddenimports=['yaml', 'sqlalchemy', 'flask_sqlalchemy', 'flask', 'flask_socketio', 'redis', 'psycopg2', 'alembic', 'pydantic', 'flask_limiter', 'flask_caching', 'python_telegram_bot'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='encoder_manager_setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
