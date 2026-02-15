from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from game_engine.config.settings import get_settings

settings = get_settings()

# create database engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base class for orm models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency function for FastAPI to get database session
    
    Yields:
        Database session that automatically closes after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
