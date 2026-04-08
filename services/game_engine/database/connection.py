from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator


# base class for orm models
class Base(DeclarativeBase):
    pass


def _get_engine():
    """Lazy engine creation to avoid import-time side effects."""
    from game_engine.config.settings import get_settings
    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


_engine = None
_SessionLocal = None


def _ensure_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = _get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _engine


def get_db() -> Generator:
    """
    Dependency function for FastAPI to get database session

    Yields:
        Database session that automatically closes after use
    """
    _ensure_engine()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    engine = _ensure_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution)"""
    engine = _ensure_engine()
    Base.metadata.drop_all(bind=engine)
