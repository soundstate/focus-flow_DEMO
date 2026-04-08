"""Playback router with in-memory state for demo purposes."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from music_control.models.track_models import PlaybackState

router = APIRouter()

# In-memory playback state per user (demo only)
_playback_state: dict[str, PlaybackState] = {}


class PlayRequest(BaseModel):
    """Request body for starting playback."""
    user_id: str = "demo_user"
    track_id: str
    track_title: str
    artist: Optional[str] = None
    playlist_id: Optional[str] = None


class UserIdRequest(BaseModel):
    """Request body with user_id only."""
    user_id: str = "demo_user"


@router.post("/play")
def play_track(request: PlayRequest):
    """Start playing a track for a user."""
    state = PlaybackState(
        user_id=request.user_id,
        track_id=request.track_id,
        track_title=request.track_title,
        artist=request.artist,
        is_playing=True,
        started_at=datetime.now(timezone.utc),
        playlist_id=request.playlist_id,
    )
    _playback_state[request.user_id] = state
    return {"status": "playing", "playback": state.model_dump()}


@router.post("/pause")
def pause_playback(request: UserIdRequest):
    """Pause playback for a user."""
    state = _playback_state.get(request.user_id)
    if not state:
        return {"status": "no_active_playback", "user_id": request.user_id}

    state.is_playing = False
    return {"status": "paused", "playback": state.model_dump()}


@router.post("/skip")
def skip_track(request: UserIdRequest):
    """Skip the current track (clears playback state)."""
    state = _playback_state.pop(request.user_id, None)
    if not state:
        return {"status": "no_active_playback", "user_id": request.user_id}

    return {"status": "skipped", "previous_track": state.track_title}


@router.get("/current")
def get_current_playback(user_id: str = "demo_user"):
    """Get the current playback state for a user."""
    state = _playback_state.get(user_id)
    if not state:
        return PlaybackState(user_id=user_id).model_dump()
    return state.model_dump()
