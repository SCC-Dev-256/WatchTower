from logging.config import fileConfig
import logging
from sqlalchemy import engine_from_config
from alembic import context

from app.core.database.models.encoder import HeloEncoder
from app.core.database.models.api_key_management import APIKey
from app.core.database.models.log_entry import LogEntry
from app.core.database.models.user import User
from app.core.database.models.encoder import Encoder
from app.core.database.models.stream_key import StreamKey
from app.core.database import db

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger('alembic.env')

def get_engine():
    try:
        # The connection string should be fetched from the app config
        return db.get_engine()
    except Exception:
        logger.info('No application found.')
        return None

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=db.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    
    engine = get_engine()
    
    if engine is None:
        raise Exception('No database engine found')

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=db.metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 