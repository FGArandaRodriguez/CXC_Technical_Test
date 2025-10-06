from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.config import settings


"""
Database session and engine configuration module.

This module initializes the synchronous SQLAlchemy engine and session factory 
used throughout the application for database interactions. It relies on 
the configuration values defined in `settings.DATABASE_URL`.

Attributes:
    engine (sqlalchemy.engine.Engine): 
        The SQLAlchemy database engine configured with connection pooling.
    SessionLocal (sqlalchemy.orm.session.sessionmaker): 
        Factory for creating new database sessions with controlled 
        commit and flush behavior.

Notes:
    The engine uses `pool_pre_ping=True` to ensure that connections 
    are valid before being used, preventing stale or dropped connections.
"""


SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)