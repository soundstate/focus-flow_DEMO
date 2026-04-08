"""Tests for Game Engine ORM models."""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game_engine.database.connection import Base
from game_engine.models.achievement_models import Achievement
from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak
from game_engine.models.xp_history_models import XPHistory


def test_achievement_table_name():
    assert Achievement.__tablename__ == "ge_user_achievements"


def test_user_level_table_name():
    assert UserLevel.__tablename__ == "ge_user_levels"


def test_user_streak_table_name():
    assert UserStreak.__tablename__ == "ge_user_streaks"


def test_xp_history_table_name():
    assert XPHistory.__tablename__ == "ge_xp_history"


def test_xp_history_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    record = XPHistory(
        user_id="user_1",
        session_id="sess_1",
        base_xp=50,
        bonus_xp=25,
        total_xp=75,
        reason="session_completed",
    )
    db.add(record)
    db.commit()
    assert record.id is not None
    db.close()
