"""Tests for AI Insights routers using FastAPI TestClient."""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models FIRST so they register with the shared Base
from ai_insights.models.insights_models import InsightCache, TokenUsage
from ai_insights.models.pattern_models import UserPattern
from ai_insights.database.connection import Base, get_db
from ai_insights.main import app


# --- test database setup using StaticPool so the same in-memory DB is shared ---
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable foreign keys for SQLite
@event.listens_for(_test_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create all tables from the shared Base metadata
Base.metadata.create_all(bind=_test_engine)

_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# Mock the SessionAnalyzer to avoid real HTTP calls
_mock_context = {
    "user_id": "user_1",
    "total_sessions": 10,
    "total_focus_minutes": 250,
    "avg_productivity_score": 0.78,
    "recent_sessions": [
        {"session_id": "s1", "duration": 25, "productivity_score": 0.8},
    ],
}


@pytest.fixture
def client():
    return TestClient(app)


@patch(
    "ai_insights.routers.insights.SessionAnalyzer.get_user_context",
    new_callable=AsyncMock,
    return_value=_mock_context,
)
def test_get_coaching(mock_ctx, client):
    """GET /api/v1/insights/users/{user_id}/coaching returns coaching tips."""
    response = client.get("/api/v1/insights/users/user_1/coaching")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_1"
    assert "tips" in data
    assert len(data["tips"]) > 0


@patch(
    "ai_insights.routers.insights.SessionAnalyzer.get_user_context",
    new_callable=AsyncMock,
    return_value=_mock_context,
)
def test_get_daily_briefing(mock_ctx, client):
    """GET /api/v1/insights/users/{user_id}/daily-briefing returns briefing."""
    response = client.get("/api/v1/insights/users/user_1/daily-briefing")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_1"
    assert "focus_plan" in data


@patch(
    "ai_insights.routers.insights.SessionAnalyzer.get_user_context",
    new_callable=AsyncMock,
    return_value=_mock_context,
)
def test_post_session_review(mock_ctx, client):
    """POST /api/v1/insights/users/{user_id}/session-review returns review."""
    session_data = {"session_id": "sess_1", "duration": 25, "productivity_score": 0.85}
    response = client.post(
        "/api/v1/insights/users/user_1/session-review",
        json=session_data,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_1"
    assert "review" in data


@patch(
    "ai_insights.routers.patterns.SessionAnalyzer.get_user_context",
    new_callable=AsyncMock,
    return_value=_mock_context,
)
def test_discover_patterns(mock_ctx, client):
    """GET /api/v1/patterns/users/{user_id}/discover returns patterns."""
    response = client.get("/api/v1/patterns/users/user_1/discover")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_1"
    assert "patterns" in data


def test_get_goals(client):
    """GET /api/v1/coaching/users/{user_id}/goals returns hardcoded goals."""
    response = client.get("/api/v1/coaching/users/user_1/goals")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_1"
    assert len(data["goals"]) == 3
    assert data["goals"][0]["title"] == "Improve focus consistency"


def test_health_check(client):
    """GET /health returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-insights"


def test_root(client):
    """GET / returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Focus Flow - AI Insights Service"
    assert data["status"] == "operational"
