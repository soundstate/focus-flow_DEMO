"""Tests for Music Control routers using TestClient."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from music_control.database.connection import Base, get_db

# Import all ORM models so Base.metadata knows about every table
from music_control.models.session_music_models import (  # noqa: F401
    YouTubeAuth, SessionMusicLog, TrackEffectiveness, UserMusicPreferences,
)

from music_control.routers import auth, playlists, playback, effectiveness


def _build_app():
    """Create a test FastAPI app with in-memory SQLite."""
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

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "music-control", "version": "1.0.0"}

    @app.get("/")
    async def root():
        return {
            "service": "Focus Flow - Music Control Service",
            "version": "1.0.0",
            "status": "operational",
            "port": 8004,
        }

    app.include_router(auth.router, prefix="/api/v1/auth")
    app.include_router(playlists.router, prefix="/api/v1/playlists")
    app.include_router(playback.router, prefix="/api/v1/playback")
    app.include_router(effectiveness.router, prefix="/api/v1/effectiveness")
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), TestSessionLocal


# ---------- Health & Root ----------

def test_health_check():
    client, _ = _build_app()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "music-control"


def test_root():
    client, _ = _build_app()
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Focus Flow - Music Control Service"
    assert data["port"] == 8004


# ---------- Playlists Router ----------

def test_list_playlists():
    client, _ = _build_app()
    response = client.get("/api/v1/playlists/")
    assert response.status_code == 200
    data = response.json()
    assert "playlists" in data
    assert len(data["playlists"]) > 0


def test_get_playlist_tracks():
    client, _ = _build_app()
    response = client.get("/api/v1/playlists/demo_focus_beats/tracks")
    assert response.status_code == 200
    data = response.json()
    assert data["playlist_id"] == "demo_focus_beats"
    assert "tracks" in data
    assert len(data["tracks"]) > 0


def test_focus_recommendations():
    client, _ = _build_app()
    response = client.get("/api/v1/playlists/focus-recommendations")
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0


# ---------- Playback Router ----------

def test_playback_play():
    client, _ = _build_app()
    response = client.post("/api/v1/playback/play", json={
        "user_id": "test_user",
        "track_id": "t1",
        "track_title": "Test Track",
        "artist": "Test Artist",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "playing"
    assert data["playback"]["track_id"] == "t1"
    assert data["playback"]["is_playing"] is True


def test_playback_pause():
    client, _ = _build_app()
    # First start playback
    client.post("/api/v1/playback/play", json={
        "user_id": "pause_user",
        "track_id": "t1",
        "track_title": "Test",
    })
    response = client.post("/api/v1/playback/pause", json={"user_id": "pause_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paused"
    assert data["playback"]["is_playing"] is False


def test_playback_pause_no_active():
    client, _ = _build_app()
    response = client.post("/api/v1/playback/pause", json={"user_id": "nobody"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_active_playback"


def test_playback_skip():
    client, _ = _build_app()
    client.post("/api/v1/playback/play", json={
        "user_id": "skip_user",
        "track_id": "t1",
        "track_title": "Skip Me",
    })
    response = client.post("/api/v1/playback/skip", json={"user_id": "skip_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "skipped"
    assert data["previous_track"] == "Skip Me"


def test_playback_skip_no_active():
    client, _ = _build_app()
    response = client.post("/api/v1/playback/skip", json={"user_id": "nobody"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "no_active_playback"


def test_playback_current():
    client, _ = _build_app()
    response = client.get("/api/v1/playback/current?user_id=idle_user")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "idle_user"
    assert data["is_playing"] is False


def test_playback_current_after_play():
    client, _ = _build_app()
    client.post("/api/v1/playback/play", json={
        "user_id": "current_user",
        "track_id": "t2",
        "track_title": "Now Playing",
        "artist": "Artist X",
    })
    response = client.get("/api/v1/playback/current?user_id=current_user")
    assert response.status_code == 200
    data = response.json()
    assert data["is_playing"] is True
    assert data["track_title"] == "Now Playing"


# ---------- Auth Router ----------

def test_auth_status_unauthenticated():
    client, _ = _build_app()
    response = client.get("/api/v1/auth/youtube/status?user_id=nobody")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is False


def test_auth_setup_and_status():
    client, _ = _build_app()
    # Setup auth
    response = client.post("/api/v1/auth/youtube/setup", json={
        "user_id": "auth_user",
        "headers": "cookie: test_cookie_value",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["user_id"] == "auth_user"

    # Check status
    response = client.get("/api/v1/auth/youtube/status?user_id=auth_user")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True


# ---------- Effectiveness Router ----------

def test_effectiveness_report_empty():
    client, _ = _build_app()
    response = client.get("/api/v1/effectiveness/users/user_new")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_new"
    assert data["total_tracks_played"] == 0


def test_effectiveness_track_missing_param():
    client, _ = _build_app()
    response = client.get("/api/v1/effectiveness/users/user_1/tracks")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_effectiveness_track_not_found():
    client, _ = _build_app()
    response = client.get("/api/v1/effectiveness/users/user_1/tracks?track_id=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data["track_id"] == "nonexistent"
    assert data["avg_productivity_score"] == 0.0
