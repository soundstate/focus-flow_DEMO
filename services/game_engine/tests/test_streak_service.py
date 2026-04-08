"""Tests for StreakService."""
from datetime import date, timedelta
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game_engine.database.connection import Base
from game_engine.models.streak_models import UserStreak
from game_engine.services.streak_service import StreakService


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_update_creates_streak_for_new_user():
    db = _make_db()
    svc = StreakService(db)
    result = svc.update("user_1")
    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak is not None
    assert streak.current_streak == 1
    assert streak.total_sessions == 1
    assert result["new_streak"] == 1
    db.close()


def test_update_increments_total_sessions():
    db = _make_db()
    svc = StreakService(db)
    svc.update("user_1")
    # same day update
    svc.update("user_1")
    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak.total_sessions == 2
    db.close()


def test_update_tracks_longest_streak():
    db = _make_db()
    svc = StreakService(db)

    # first session
    svc.update("user_1")
    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak.longest_streak == 1

    # simulate next-day session by patching date.today()
    with patch("game_engine.calculators.streak_calculator.date") as mock_date:
        mock_date.today.return_value = date.today() + timedelta(days=1)
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        with patch("game_engine.services.streak_service.date") as mock_svc_date:
            mock_svc_date.today.return_value = date.today() + timedelta(days=1)
            mock_svc_date.side_effect = lambda *a, **kw: date(*a, **kw)
            svc.update("user_1")

    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak.longest_streak == 2
    assert streak.current_streak == 2
    db.close()


def test_get_streak_none():
    db = _make_db()
    svc = StreakService(db)
    assert svc.get_streak("nonexistent") is None
    db.close()


def test_get_streak_existing():
    db = _make_db()
    svc = StreakService(db)
    svc.update("user_1")
    streak = svc.get_streak("user_1")
    assert streak is not None
    assert streak.user_id == "user_1"
    db.close()


def test_streak_sets_start_date():
    db = _make_db()
    svc = StreakService(db)
    svc.update("user_1")
    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak.streak_start_date == date.today()
    db.close()
