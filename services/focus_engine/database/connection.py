"""
Focus Engine Database Connection
SQLAlchemy setup with connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from config.settings import get_settings
import logging

logger = logging.getLogger("focus_engine.database")
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.debug_mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Modern declarative base (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass


def get_db() -> Session:
    """Get database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Backwards-compatible alias
get_database = get_db
