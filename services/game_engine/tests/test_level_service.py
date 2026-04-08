"""Tests for LevelService."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game_engine.database.connection import Base
from game_engine.models.level_models import UserLevel
from game_engine.models.xp_history_models import XPHistory
from game_engine.services.level_service import LevelService


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_award_xp_creates_user_level():
    db = _make_db()
    svc = LevelService(db)
    svc.award_xp("user_1", "sess_1", 50, 25, 75, "session_completed")
    level = db.query(UserLevel).filter_by(user_id="user_1").first()
    assert level is not None
    assert level.total_xp == 75
    db.close()


def test_award_xp_records_history():
    db = _make_db()
    svc = LevelService(db)
    svc.award_xp("user_1", "sess_1", 50, 25, 75, "session_completed")
    history = db.query(XPHistory).filter_by(user_id="user_1").all()
    assert len(history) == 1
    db.close()


def test_level_up():
    db = _make_db()
    svc = LevelService(db)
    result = svc.award_xp("user_1", "sess_1", 150, 0, 150, "session_completed")
    level = db.query(UserLevel).filter_by(user_id="user_1").first()
    assert level.current_level >= 2
    assert result["level_up"] is True
    db.close()


def test_get_user_level_none():
    db = _make_db()
    svc = LevelService(db)
    assert svc.get_user_level("nonexistent") is None
    db.close()


def test_get_user_level_existing():
    db = _make_db()
    svc = LevelService(db)
    svc.award_xp("user_1", "sess_1", 50, 0, 50, "session_completed")
    level = svc.get_user_level("user_1")
    assert level is not None
    assert level.user_id == "user_1"
    db.close()


def test_get_xp_history():
    db = _make_db()
    svc = LevelService(db)
    svc.award_xp("user_1", "sess_1", 50, 0, 50, "session_completed")
    svc.award_xp("user_1", "sess_2", 60, 10, 70, "session_completed")
    history = svc.get_xp_history("user_1")
    assert len(history) == 2
    db.close()


def test_award_xp_accumulates():
    db = _make_db()
    svc = LevelService(db)
    svc.award_xp("user_1", "sess_1", 30, 0, 30, "session_completed")
    svc.award_xp("user_1", "sess_2", 40, 0, 40, "session_completed")
    level = db.query(UserLevel).filter_by(user_id="user_1").first()
    assert level.total_xp == 70
    db.close()
