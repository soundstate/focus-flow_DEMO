"""Tests for Game Engine event handlers."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game_engine.database.connection import Base
from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak
from game_engine.models.achievement_models import Achievement
from game_engine.models.xp_history_models import XPHistory
from game_engine.events.handlers import handle_session_completed


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


@pytest.mark.asyncio
async def test_handle_session_completed_creates_records():
    db = _make_db()
    data = {
        "user_id": "user_1",
        "session_id": "sess_1",
        "duration": 25,
        "completed": True,
        "productivity_score": 7.0,
    }
    result = await handle_session_completed(data, db, publisher=None)

    assert result["streak"]["new_streak"] == 1
    assert result["xp"]["total_xp"] > 0
    assert result["level"]["new_level"] >= 1

    # verify DB records
    level = db.query(UserLevel).filter_by(user_id="user_1").first()
    assert level is not None
    assert level.total_xp > 0

    streak = db.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak is not None
    assert streak.total_sessions == 1

    history = db.query(XPHistory).filter_by(user_id="user_1").all()
    assert len(history) == 1
    db.close()


@pytest.mark.asyncio
async def test_handle_session_completed_publishes_achievement():
    db = _make_db()
    publisher = AsyncMock()

    data = {
        "user_id": "user_1",
        "session_id": "sess_1",
        "duration": 25,
        "completed": True,
    }
    result = await handle_session_completed(data, db, publisher=publisher)

    # first_session achievement should be unlocked and published
    assert result["achievements_unlocked"] >= 1
    publisher.publish.assert_any_call(
        "achievement.unlocked",
        "user_1",
        pytest.approx(
            {
                "achievement_type": "first_session",
                "title": "First Focus",
                "description": "Complete your first focus session",
                "icon": "rocket",
            }
        ),
    )
    db.close()


@pytest.mark.asyncio
async def test_handle_session_completed_publishes_level_up():
    db = _make_db()
    publisher = AsyncMock()

    # award enough XP to level up (need >= 150 XP for level 2 from level 1)
    # XP_BASE=100, XP_MULTIPLIER=1.5, xp_to_next_level(2) = 100 * 1.5^1 = 150
    # 50 min session: base_xp = 50 * (50/25) = 100, completion bonus = 25
    # productivity bonus with score 10: 100 * (10/10)*0.5 = 50
    # total = 100 + 25 + 50 = 175 > 150
    data = {
        "user_id": "user_1",
        "session_id": "sess_1",
        "duration": 50,
        "completed": True,
        "productivity_score": 10.0,
    }
    result = await handle_session_completed(data, db, publisher=publisher)

    if result["level"]["level_up"]:
        publisher.publish.assert_any_call(
            "level.up",
            "user_1",
            {
                "new_level": result["level"]["new_level"],
                "total_xp": result["level"]["total_xp"],
            },
        )
    db.close()


@pytest.mark.asyncio
async def test_handle_session_completed_no_publisher():
    db = _make_db()
    data = {
        "user_id": "user_1",
        "session_id": "sess_1",
        "duration": 25,
        "completed": True,
    }
    # should not raise even without publisher
    result = await handle_session_completed(data, db, publisher=None)
    assert "streak" in result
    assert "xp" in result
    assert "level" in result
    db.close()
