"""Tests for LeaderboardService."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from game_engine.database.connection import Base
from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak
from game_engine.services.leaderboard_service import LeaderboardService


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


@pytest.mark.asyncio
async def test_xp_leaderboard_empty():
    db = _make_db()
    svc = LeaderboardService(db)
    result = await svc.get_xp_leaderboard()
    assert result == []
    db.close()


@pytest.mark.asyncio
async def test_xp_leaderboard_ordering():
    db = _make_db()
    db.add(UserLevel(user_id="u1", current_level=2, current_xp=50, total_xp=200, xp_to_next_level=150))
    db.add(UserLevel(user_id="u2", current_level=5, current_xp=10, total_xp=500, xp_to_next_level=300))
    db.add(UserLevel(user_id="u3", current_level=1, current_xp=20, total_xp=20, xp_to_next_level=100))
    db.commit()

    svc = LeaderboardService(db)
    result = await svc.get_xp_leaderboard()
    assert len(result) == 3
    assert result[0]["user_id"] == "u2"
    assert result[0]["rank"] == 1
    assert result[1]["user_id"] == "u1"
    assert result[2]["user_id"] == "u3"
    db.close()


@pytest.mark.asyncio
async def test_streak_leaderboard_empty():
    db = _make_db()
    svc = LeaderboardService(db)
    result = await svc.get_streak_leaderboard()
    assert result == []
    db.close()


@pytest.mark.asyncio
async def test_streak_leaderboard_ordering():
    db = _make_db()
    db.add(UserStreak(user_id="u1", current_streak=5, longest_streak=10, total_sessions=20))
    db.add(UserStreak(user_id="u2", current_streak=15, longest_streak=15, total_sessions=30))
    db.commit()

    svc = LeaderboardService(db)
    result = await svc.get_streak_leaderboard()
    assert len(result) == 2
    assert result[0]["user_id"] == "u2"
    assert result[0]["rank"] == 1
    assert result[1]["user_id"] == "u1"
    db.close()


@pytest.mark.asyncio
async def test_xp_leaderboard_limit():
    db = _make_db()
    for i in range(10):
        db.add(UserLevel(user_id=f"u{i}", current_level=1, current_xp=0, total_xp=i * 100, xp_to_next_level=100))
    db.commit()

    svc = LeaderboardService(db)
    result = await svc.get_xp_leaderboard(limit=3)
    assert len(result) == 3
    db.close()
