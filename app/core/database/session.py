from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import DatabaseSettings

# Create engine using the database URL from settings
engine = create_engine(DatabaseSettings().DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 