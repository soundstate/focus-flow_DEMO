"""Music Control ORM models for YouTube auth, session music logs, and effectiveness tracking."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON
from datetime import datetime, timezone

from music_control.database.connection import Base


def _utcnow():
    """Return timezone-aware UTC now."""
    return datetime.now(timezone.utc)


class YouTubeAuth(Base):
    """YouTube Music authentication credentials per user."""
    __tablename__ = "mc_youtube_auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    credentials = Column(JSON, nullable=True)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class SessionMusicLog(Base):
    """Log of tracks played during focus sessions."""
    __tablename__ = "mc_session_music_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    track_id = Column(String, nullable=False)
    track_title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    playlist_id = Column(String, nullable=True)
    started_at = Column(DateTime, default=_utcnow)
    ended_at = Column(DateTime, nullable=True)


class TrackEffectiveness(Base):
    """Aggregated effectiveness scores for tracks per user."""
    __tablename__ = "mc_track_effectiveness"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    track_id = Column(String, nullable=False)
    genre = Column(String, nullable=True)
    avg_productivity_score = Column(Float, default=0.0)
    session_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class UserMusicPreferences(Base):
    """Per-user music preferences and settings."""
    __tablename__ = "mc_user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    auto_play = Column(Boolean, default=True)
    preferred_genres = Column(JSON, default=list)
    favorite_playlists = Column(JSON, default=list)
    created_at = Column(DateTime, default=_utcnow)
