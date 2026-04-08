"""Tests for Music Control ORM models and Pydantic schemas."""
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from music_control.database.connection import Base
from music_control.models.session_music_models import (
    YouTubeAuth,
    SessionMusicLog,
    TrackEffectiveness,
    UserMusicPreferences,
)
from music_control.models.playlist_models import PlaylistInfo, TrackInfo
from music_control.models.track_models import (
    PlaybackState,
    TrackEffectivenessReport,
    EffectivenessReport,
)


# ---------- ORM table names ----------

def test_youtube_auth_table_name():
    assert YouTubeAuth.__tablename__ == "mc_youtube_auth"


def test_session_music_log_table_name():
    assert SessionMusicLog.__tablename__ == "mc_session_music_log"


def test_track_effectiveness_table_name():
    assert TrackEffectiveness.__tablename__ == "mc_track_effectiveness"


def test_user_preferences_table_name():
    assert UserMusicPreferences.__tablename__ == "mc_user_preferences"


# ---------- ORM CRUD ----------

def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_youtube_auth_create():
    db = _make_db()
    auth = YouTubeAuth(
        user_id="user_1",
        credentials={"cookie": "abc123"},
        is_valid=True,
    )
    db.add(auth)
    db.commit()
    assert auth.id is not None
    assert auth.user_id == "user_1"
    assert auth.credentials == {"cookie": "abc123"}
    assert auth.is_valid is True
    assert auth.created_at is not None
    db.close()


def test_youtube_auth_user_id_unique():
    db = _make_db()
    auth1 = YouTubeAuth(user_id="user_1", credentials={})
    db.add(auth1)
    db.commit()
    auth2 = YouTubeAuth(user_id="user_1", credentials={})
    db.add(auth2)
    try:
        db.commit()
        assert False, "Should have raised IntegrityError"
    except Exception:
        db.rollback()
    db.close()


def test_session_music_log_create():
    db = _make_db()
    log = SessionMusicLog(
        user_id="user_1",
        session_id="session_abc",
        track_id="track_xyz",
        track_title="Lo-fi Beats",
        artist="ChillHop",
        playlist_id="playlist_1",
    )
    db.add(log)
    db.commit()
    assert log.id is not None
    assert log.track_title == "Lo-fi Beats"
    assert log.artist == "ChillHop"
    assert log.started_at is not None
    db.close()


def test_track_effectiveness_create():
    db = _make_db()
    eff = TrackEffectiveness(
        user_id="user_1",
        track_id="track_xyz",
        genre="lo-fi",
        avg_productivity_score=0.85,
        session_count=5,
    )
    db.add(eff)
    db.commit()
    assert eff.id is not None
    assert eff.avg_productivity_score == 0.85
    assert eff.session_count == 5
    db.close()


def test_user_preferences_create():
    db = _make_db()
    prefs = UserMusicPreferences(
        user_id="user_1",
        auto_play=True,
        preferred_genres=["lo-fi", "ambient"],
        favorite_playlists=["playlist_1", "playlist_2"],
    )
    db.add(prefs)
    db.commit()
    assert prefs.id is not None
    assert prefs.auto_play is True
    assert prefs.preferred_genres == ["lo-fi", "ambient"]
    assert prefs.favorite_playlists == ["playlist_1", "playlist_2"]
    db.close()


def test_user_preferences_user_id_unique():
    db = _make_db()
    prefs1 = UserMusicPreferences(user_id="user_1")
    db.add(prefs1)
    db.commit()
    prefs2 = UserMusicPreferences(user_id="user_1")
    db.add(prefs2)
    try:
        db.commit()
        assert False, "Should have raised IntegrityError"
    except Exception:
        db.rollback()
    db.close()


# ---------- Pydantic models ----------

def test_playlist_info():
    info = PlaylistInfo(
        playlist_id="pl_1",
        title="Focus Beats",
        description="Great for concentration",
        track_count=25,
        thumbnail_url="https://example.com/thumb.jpg",
    )
    assert info.playlist_id == "pl_1"
    assert info.title == "Focus Beats"
    assert info.track_count == 25


def test_playlist_info_defaults():
    info = PlaylistInfo(playlist_id="pl_2", title="Ambient")
    assert info.description is None
    assert info.track_count == 0
    assert info.thumbnail_url is None


def test_track_info():
    track = TrackInfo(
        track_id="t_1",
        title="Midnight Rain",
        artist="Chill Producer",
        album="Night Sessions",
        duration_seconds=240,
    )
    assert track.track_id == "t_1"
    assert track.artist == "Chill Producer"
    assert track.duration_seconds == 240


def test_track_info_defaults():
    track = TrackInfo(track_id="t_2", title="Morning Dew")
    assert track.artist == "Unknown"
    assert track.album is None
    assert track.duration_seconds is None


def test_playback_state():
    state = PlaybackState(
        user_id="user_1",
        track_id="t_1",
        track_title="Focus Time",
        artist="Producer X",
        is_playing=True,
        playlist_id="pl_1",
    )
    assert state.user_id == "user_1"
    assert state.is_playing is True
    assert state.track_title == "Focus Time"


def test_playback_state_defaults():
    state = PlaybackState(user_id="user_1")
    assert state.track_id is None
    assert state.is_playing is False
    assert state.started_at is None


def test_track_effectiveness_report():
    report = TrackEffectivenessReport(
        track_id="t_1",
        genre="lo-fi",
        avg_productivity_score=0.9,
        session_count=10,
    )
    assert report.track_id == "t_1"
    assert report.avg_productivity_score == 0.9


def test_effectiveness_report():
    report = EffectivenessReport(
        user_id="user_1",
        total_tracks_played=50,
        top_tracks=[
            TrackEffectivenessReport(
                track_id="t_1",
                genre="lo-fi",
                avg_productivity_score=0.92,
                session_count=8,
            )
        ],
        top_genres=[{"genre": "lo-fi", "avg_score": 0.88}],
        avg_overall_score=0.82,
    )
    assert report.total_tracks_played == 50
    assert len(report.top_tracks) == 1
    assert report.top_tracks[0].track_id == "t_1"
    assert report.avg_overall_score == 0.82


def test_effectiveness_report_defaults():
    report = EffectivenessReport(user_id="user_1")
    assert report.total_tracks_played == 0
    assert report.top_tracks == []
    assert report.top_genres == []
    assert report.avg_overall_score == 0.0
