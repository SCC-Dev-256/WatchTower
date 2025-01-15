from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database.session import SessionLocal
from app.core.database.models.encoder import Base
from sqlalchemy import create_engine
import pytest

def get_test_database_url() -> str:
    """Get test database URL"""
    return "postgresql://test_user:test_pass@localhost/test_encoder_db"

@contextmanager
def get_test_db() -> Generator[Session, None, None]:
    """Get test database session"""
    engine = create_engine(get_test_database_url())
    TestingSessionLocal = SessionLocal(bind=engine)
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_db():
    """Pytest fixture for test database"""
    engine = create_engine(get_test_database_url())
    Base.metadata.create_all(bind=engine)
    with get_test_db() as db:
        yield db
    Base.metadata.drop_all(bind=engine)