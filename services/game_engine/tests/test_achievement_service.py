"""Tests for AchievementService."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game_engine.database.connection import Base
from game_engine.models.achievement_models import Achievement, AchievementType
from game_engine.services.achievement_service import AchievementService


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_ensure_achievements_creates_rows():
    db = _make_db()
    svc = AchievementService(db)
    svc._ensure_achievements_exist("user_1")
    achievements = db.query(Achievement).filter_by(user_id="user_1").all()
    assert len(achievements) == len(AchievementType)
    db.close()


def test_ensure_achievements_idempotent():
    db = _make_db()
    svc = AchievementService(db)
    svc._ensure_achievements_exist("user_1")
    svc._ensure_achievements_exist("user_1")
    achievements = db.query(Achievement).filter_by(user_id="user_1").all()
    assert len(achievements) == len(AchievementType)
    db.close()


def test_evaluate_unlocks_first_session():
    db = _make_db()
    svc = AchievementService(db)
    session_data = {
        "total_sessions": 1,
        "current_streak": 1,
        "session_completed": True,
    }
    newly_unlocked = svc.evaluate("user_1", session_data)
    # first_session should be unlocked
    types_unlocked = [a.achievement_type for a in newly_unlocked]
    assert AchievementType.FIRST_SESSION in types_unlocked
    db.close()


def test_evaluate_does_not_re_unlock():
    db = _make_db()
    svc = AchievementService(db)
    session_data = {
        "total_sessions": 1,
        "current_streak": 1,
        "session_completed": True,
    }
    first_run = svc.evaluate("user_1", session_data)
    second_run = svc.evaluate("user_1", session_data)
    # second evaluation should not unlock already-unlocked achievements
    first_types = {a.achievement_type for a in first_run}
    second_types = {a.achievement_type for a in second_run}
    assert len(second_types & first_types) == 0
    db.close()


def test_evaluate_streak_achievements():
    db = _make_db()
    svc = AchievementService(db)
    session_data = {
        "total_sessions": 5,
        "current_streak": 3,
        "session_completed": True,
    }
    newly_unlocked = svc.evaluate("user_1", session_data)
    types_unlocked = [a.achievement_type for a in newly_unlocked]
    assert AchievementType.STREAK_3 in types_unlocked
    db.close()


def test_get_user_achievements():
    db = _make_db()
    svc = AchievementService(db)
    svc._ensure_achievements_exist("user_1")
    achievements = svc.get_user_achievements("user_1")
    assert len(achievements) == len(AchievementType)
    db.close()


def test_get_stats():
    db = _make_db()
    svc = AchievementService(db)
    session_data = {
        "total_sessions": 1,
        "current_streak": 1,
        "session_completed": True,
    }
    svc.evaluate("user_1", session_data)
    stats = svc.get_stats("user_1")
    assert stats["total_available"] == len(AchievementType)
    assert stats["total_unlocked"] >= 1
    assert 0 <= stats["completion_percentage"] <= 100
    db.close()
