"""Tests for YouTube Music client."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from music_control.database.connection import Base
from music_control.clients.youtube_music_client import YouTubeMusicClient
from music_control.models.session_music_models import YouTubeAuth


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_client_returns_demo_playlists():
    """Without ytmusicapi auth, client should return demo data."""
    client = YouTubeMusicClient()
    playlists = client.get_playlists()
    assert isinstance(playlists, list)
    assert len(playlists) == 3
    assert playlists[0]["playlist_id"] == "demo_focus_beats"


def test_client_returns_demo_tracks():
    client = YouTubeMusicClient()
    tracks = client.get_playlist_tracks("demo_focus_beats")
    assert isinstance(tracks, list)
    assert len(tracks) == 3
    assert tracks[0]["title"] == "Midnight Rain"


def test_client_returns_demo_tracks_ambient():
    client = YouTubeMusicClient()
    tracks = client.get_playlist_tracks("demo_ambient_flow")
    assert isinstance(tracks, list)
    assert len(tracks) == 2


def test_client_returns_generic_tracks_for_unknown():
    client = YouTubeMusicClient()
    tracks = client.get_playlist_tracks("unknown_playlist_id")
    assert isinstance(tracks, list)
    assert len(tracks) == 1
    assert tracks[0]["track_id"] == "demo_generic_1"


def test_setup_auth():
    db = _make_db()
    result = YouTubeMusicClient.setup_auth(db, "user_1", "cookie: abc123")
    assert result["status"] == "ok"
    assert result["user_id"] == "user_1"

    auth = db.query(YouTubeAuth).filter_by(user_id="user_1").first()
    assert auth is not None
    assert auth.credentials == {"headers": "cookie: abc123"}
    assert auth.is_valid is True
    db.close()


def test_setup_auth_update_existing():
    db = _make_db()
    YouTubeMusicClient.setup_auth(db, "user_1", "old_headers")
    YouTubeMusicClient.setup_auth(db, "user_1", "new_headers")

    auths = db.query(YouTubeAuth).filter_by(user_id="user_1").all()
    assert len(auths) == 1
    assert auths[0].credentials == {"headers": "new_headers"}
    db.close()


def test_check_auth_status_not_found():
    db = _make_db()
    result = YouTubeMusicClient.check_auth_status(db, "nobody")
    assert result["authenticated"] is False
    assert result["user_id"] == "nobody"
    db.close()


def test_check_auth_status_found():
    db = _make_db()
    YouTubeMusicClient.setup_auth(db, "user_1", "headers_data")
    result = YouTubeMusicClient.check_auth_status(db, "user_1")
    assert result["authenticated"] is True
    assert result["user_id"] == "user_1"
    assert "created_at" in result
    db.close()
