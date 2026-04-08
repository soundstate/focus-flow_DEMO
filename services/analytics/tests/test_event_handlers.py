"""Tests for Analytics event handlers."""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics.database.connection import Base
from analytics.models.metrics_models import DailyAggregate
from analytics.events.handlers import (
    handle_session_completed,
    handle_achievement_unlocked,
    handle_level_up,
)


def _make_db():
    """Create a fresh in-memory SQLite session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.mark.asyncio
async def test_handle_session_completed_creates_aggregate():
    db = _make_db()
    data = {
        "user_id": "user_evt",
        "duration": 25,
        "productivity_score": 0.9,
        "xp_earned": 100,
        "interruptions": 1,
    }
    await handle_session_completed(data, db)

    agg = db.query(DailyAggregate).filter_by(user_id="user_evt").first()
    assert agg is not None
    assert agg.total_sessions == 1
    assert agg.total_focus_minutes == 25
    assert agg.total_xp_earned == 100
    db.close()


@pytest.mark.asyncio
async def test_handle_session_completed_increments():
    db = _make_db()
    data1 = {
        "user_id": "user_evt2",
        "duration": 25,
        "productivity_score": 0.8,
        "xp_earned": 100,
    }
    data2 = {
        "user_id": "user_evt2",
        "duration": 50,
        "productivity_score": 0.6,
        "xp_earned": 200,
    }
    await handle_session_completed(data1, db)
    await handle_session_completed(data2, db)

    agg = db.query(DailyAggregate).filter_by(user_id="user_evt2").first()
    assert agg.total_sessions == 2
    assert agg.total_focus_minutes == 75
    assert agg.total_xp_earned == 300
    db.close()


@pytest.mark.asyncio
async def test_handle_session_completed_missing_user_id():
    """Handler should skip gracefully when user_id is missing."""
    db = _make_db()
    data = {"duration": 25}
    await handle_session_completed(data, db)

    rows = db.query(DailyAggregate).all()
    assert len(rows) == 0
    db.close()


@pytest.mark.asyncio
async def test_handle_achievement_unlocked_logs(caplog):
    """Achievement handler logs the event without errors."""
    db = _make_db()
    import logging
    with caplog.at_level(logging.INFO, logger="analytics.events.handlers"):
        await handle_achievement_unlocked(
            {"user_id": "u1", "achievement_type": "streak_3"}, db
        )
    assert "Achievement unlocked" in caplog.text
    db.close()


@pytest.mark.asyncio
async def test_handle_level_up_logs(caplog):
    """Level-up handler logs the event without errors."""
    db = _make_db()
    import logging
    with caplog.at_level(logging.INFO, logger="analytics.events.handlers"):
        await handle_level_up(
            {"user_id": "u1", "new_level": 5}, db
        )
    assert "Level up" in caplog.text
    db.close()
