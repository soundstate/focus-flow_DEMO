"""Tests for Game Engine routers using FastAPI TestClient."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from game_engine.database.connection import Base, get_db
from game_engine.routers import achievements, levels, streaks, leaderboards

# Import models so Base.metadata knows about all tables
from game_engine.models.achievement_models import Achievement  # noqa: F401
from game_engine.models.level_models import UserLevel  # noqa: F401
from game_engine.models.streak_models import UserStreak  # noqa: F401
from game_engine.models.xp_history_models import XPHistory  # noqa: F401


def _build_app():
    """Create a test FastAPI app with in-memory SQLite.

    Uses StaticPool so all connections share the same in-memory database.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(achievements.router, prefix="/api/v1/achievements")
    app.include_router(levels.router, prefix="/api/v1/levels")
    app.include_router(streaks.router, prefix="/api/v1/streaks")
    app.include_router(leaderboards.router, prefix="/api/v1/leaderboards")
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# --- Achievement routes ---


def test_get_user_achievements():
    client = _build_app()
    resp = client.get("/api/v1/achievements/users/user_1")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0  # achievements are auto-created


def test_get_recent_achievements_empty():
    client = _build_app()
    resp = client.get("/api/v1/achievements/users/user_1/recent")
    assert resp.status_code == 200
    assert resp.json() == []  # none unlocked yet


def test_get_achievement_stats():
    client = _build_app()
    resp = client.get("/api/v1/achievements/users/user_1/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_unlocked" in data
    assert "total_available" in data


# --- Level routes ---


def test_get_user_level_not_found():
    client = _build_app()
    resp = client.get("/api/v1/levels/users/nonexistent")
    assert resp.status_code == 404


def test_process_session():
    client = _build_app()
    resp = client.post(
        "/api/v1/levels/process-session",
        json={
            "user_id": "user_1",
            "session_id": "sess_1",
            "session_duration": 25,
            "session_completed": True,
            "productivity_score": 7.0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "streak" in data
    assert "xp" in data
    assert "level" in data
    assert "achievements_unlocked" in data


def test_process_session_then_get_level():
    client = _build_app()
    # process a session first
    client.post(
        "/api/v1/levels/process-session",
        json={
            "user_id": "user_1",
            "session_id": "sess_1",
            "session_duration": 25,
            "session_completed": True,
        },
    )
    resp = client.get("/api/v1/levels/users/user_1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_level"] >= 1
    assert data["total_xp"] > 0


def test_get_xp_history():
    client = _build_app()
    # process a session first
    client.post(
        "/api/v1/levels/process-session",
        json={
            "user_id": "user_1",
            "session_id": "sess_1",
            "session_duration": 25,
            "session_completed": True,
        },
    )
    resp = client.get("/api/v1/levels/users/user_1/history")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


# --- Streak routes ---


def test_get_user_streak_not_found():
    client = _build_app()
    resp = client.get("/api/v1/streaks/users/nonexistent")
    assert resp.status_code == 404


def test_get_user_streak_after_session():
    client = _build_app()
    # process a session to create streak
    client.post(
        "/api/v1/levels/process-session",
        json={
            "user_id": "user_1",
            "session_id": "sess_1",
            "session_duration": 25,
            "session_completed": True,
        },
    )
    resp = client.get("/api/v1/streaks/users/user_1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] >= 1
    assert "is_active" in data
    assert "days_until_break" in data


# --- Leaderboard routes ---


def test_xp_leaderboard_empty():
    client = _build_app()
    resp = client.get("/api/v1/leaderboards/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_streak_leaderboard_empty():
    client = _build_app()
    resp = client.get("/api/v1/leaderboards/streaks")
    assert resp.status_code == 200
    assert resp.json() == []


def test_leaderboard_after_sessions():
    client = _build_app()
    # create some user data
    for i in range(3):
        client.post(
            "/api/v1/levels/process-session",
            json={
                "user_id": f"user_{i}",
                "session_id": f"sess_{i}",
                "session_duration": 25 * (i + 1),
                "session_completed": True,
            },
        )
    resp = client.get("/api/v1/leaderboards/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # highest XP should be rank 1
    assert data[0]["rank"] == 1
