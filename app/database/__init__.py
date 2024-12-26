from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import Session
from contextlib import contextmanager
from typing import Generator
from app.config.config import settings

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize database and migrations"""
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Database session context manager"""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close() 