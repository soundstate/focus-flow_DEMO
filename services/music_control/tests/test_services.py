"""Tests for Music Control services: PlaylistService and EffectivenessTracker."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from music_control.database.connection import Base
from music_control.services.playlist_service import PlaylistService
from music_control.services.effectiveness_tracker import EffectivenessTracker
from music_control.clients.youtube_music_client import YouTubeMusicClient
from music_control.models.session_music_models import TrackEffectiveness, SessionMusicLog


def _make_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


# ---------- PlaylistService ----------

def test_playlist_service_get_playlists():
    service = PlaylistService()
    playlists = service.get_playlists()
    assert isinstance(playlists, list)
    assert len(playlists) > 0
    assert "playlist_id" in playlists[0]
    assert "title" in playlists[0]


def test_playlist_service_get_playlist_tracks():
    service = PlaylistService()
    tracks = service.get_playlist_tracks("demo_focus_beats")
    assert isinstance(tracks, list)
    assert len(tracks) > 0
    assert "track_id" in tracks[0]
    assert "title" in tracks[0]


def test_playlist_service_get_focus_recommendations():
    service = PlaylistService()
    recs = service.get_focus_recommendations()
    assert isinstance(recs, list)
    assert len(recs) > 0
    # All demo playlists have focus-related keywords
    for rec in recs:
        title = rec.get("title", "").lower()
        desc = rec.get("description", "").lower()
        combined = title + " " + desc
        has_keyword = any(
            kw in combined
            for kw in ["focus", "ambient", "classical", "chill", "lo-fi", "flow", "concentration"]
        )
        assert has_keyword, f"Playlist '{rec['title']}' should match focus keywords"


def test_playlist_service_tracks_for_unknown_playlist():
    service = PlaylistService()
    tracks = service.get_playlist_tracks("nonexistent_playlist")
    assert isinstance(tracks, list)
    # Should return generic demo tracks
    assert len(tracks) > 0


# ---------- EffectivenessTracker ----------

def test_effectiveness_tracker_empty_report():
    db = _make_db()
    tracker = EffectivenessTracker(db)
    report = tracker.get_report("user_new")
    assert report["user_id"] == "user_new"
    assert report["total_tracks_played"] == 0
    assert report["top_tracks"] == []
    assert report["avg_overall_score"] == 0.0
    db.close()


def test_effectiveness_tracker_log_session_music():
    db = _make_db()
    tracker = EffectivenessTracker(db)
    result = tracker.log_session_music(
        user_id="user_1",
        session_id="session_1",
        track_id="track_1",
        track_title="Test Track",
        artist="Test Artist",
        playlist_id="playlist_1",
        productivity_score=0.85,
        genre="lo-fi",
    )
    assert result["status"] == "logged"
    assert result["log_id"] is not None

    # Verify the log was created
    log = db.query(SessionMusicLog).filter_by(user_id="user_1").first()
    assert log is not None
    assert log.track_title == "Test Track"

    # Verify effectiveness was created
    eff = db.query(TrackEffectiveness).filter_by(user_id="user_1", track_id="track_1").first()
    assert eff is not None
    assert eff.avg_productivity_score == 0.85
    assert eff.session_count == 1
    db.close()


def test_effectiveness_tracker_update_running_average():
    db = _make_db()
    tracker = EffectivenessTracker(db)

    # Log first session
    tracker.log_session_music(
        user_id="user_1",
        session_id="s1",
        track_id="t1",
        track_title="Track 1",
        productivity_score=0.80,
        genre="lo-fi",
    )

    # Log second session with same track
    tracker.log_session_music(
        user_id="user_1",
        session_id="s2",
        track_id="t1",
        track_title="Track 1",
        productivity_score=0.90,
        genre="lo-fi",
    )

    eff = db.query(TrackEffectiveness).filter_by(user_id="user_1", track_id="t1").first()
    assert eff.session_count == 2
    # Running average: (0.80 + 0.90) / 2 = 0.85
    assert abs(eff.avg_productivity_score - 0.85) < 0.01
    db.close()


def test_effectiveness_tracker_get_report_with_data():
    db = _make_db()
    tracker = EffectivenessTracker(db)

    # Log multiple tracks
    tracker.log_session_music(
        user_id="user_1", session_id="s1", track_id="t1",
        track_title="Track 1", productivity_score=0.90, genre="lo-fi",
    )
    tracker.log_session_music(
        user_id="user_1", session_id="s2", track_id="t2",
        track_title="Track 2", productivity_score=0.70, genre="ambient",
    )

    report = tracker.get_report("user_1")
    assert report["user_id"] == "user_1"
    assert report["total_tracks_played"] == 2
    assert len(report["top_tracks"]) == 2
    # Top track should be the one with higher score
    assert report["top_tracks"][0]["track_id"] == "t1"
    assert len(report["top_genres"]) == 2
    assert report["avg_overall_score"] > 0
    db.close()


def test_effectiveness_tracker_get_track_report():
    db = _make_db()
    tracker = EffectivenessTracker(db)

    tracker.log_session_music(
        user_id="user_1", session_id="s1", track_id="t1",
        track_title="Track 1", productivity_score=0.88, genre="lo-fi",
    )

    report = tracker.get_track_report("user_1", "t1")
    assert report["track_id"] == "t1"
    assert report["avg_productivity_score"] == 0.88
    assert report["session_count"] == 1
    db.close()


def test_effectiveness_tracker_get_track_report_not_found():
    db = _make_db()
    tracker = EffectivenessTracker(db)
    report = tracker.get_track_report("user_1", "nonexistent")
    assert report["track_id"] == "nonexistent"
    assert report["avg_productivity_score"] == 0.0
    assert report["session_count"] == 0
    db.close()


def test_effectiveness_tracker_log_without_score():
    db = _make_db()
    tracker = EffectivenessTracker(db)
    result = tracker.log_session_music(
        user_id="user_1",
        session_id="s1",
        track_id="t1",
        track_title="Track 1",
    )
    assert result["status"] == "logged"
    # No effectiveness record should be created when score is None
    eff = db.query(TrackEffectiveness).filter_by(user_id="user_1", track_id="t1").first()
    assert eff is None
    db.close()
