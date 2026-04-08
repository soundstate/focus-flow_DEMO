"""Pydantic models for playback state and effectiveness reporting."""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PlaybackState(BaseModel):
    """Current playback state for a user."""
    user_id: str
    track_id: Optional[str] = None
    track_title: Optional[str] = None
    artist: Optional[str] = None
    is_playing: bool = False
    started_at: Optional[datetime] = None
    playlist_id: Optional[str] = None


class TrackEffectivenessReport(BaseModel):
    """Effectiveness data for a single track."""
    track_id: str
    genre: Optional[str] = None
    avg_productivity_score: float = 0.0
    session_count: int = 0


class EffectivenessReport(BaseModel):
    """Overall effectiveness report for a user."""
    user_id: str
    total_tracks_played: int = 0
    top_tracks: list[TrackEffectivenessReport] = []
    top_genres: list[dict] = []
    avg_overall_score: float = 0.0
