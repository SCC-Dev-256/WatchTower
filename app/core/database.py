from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Create the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the app context"""
    db.init_app(app)  # Initialize the db with the app context

def get_db_session(app):
    """Get a scoped database session"""
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    return db_session 