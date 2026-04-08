"""Pydantic models for playlist and track information."""

from pydantic import BaseModel
from typing import Optional


class PlaylistInfo(BaseModel):
    """Playlist metadata returned by the YouTube Music client."""
    playlist_id: str
    title: str
    description: Optional[str] = None
    track_count: int = 0
    thumbnail_url: Optional[str] = None


class TrackInfo(BaseModel):
    """Track metadata within a playlist."""
    track_id: str
    title: str
    artist: str = "Unknown"
    album: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
