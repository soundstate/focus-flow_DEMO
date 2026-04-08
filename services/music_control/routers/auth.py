"""Authentication router for YouTube Music credentials."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from music_control.database.connection import get_db
from music_control.clients.youtube_music_client import YouTubeMusicClient

router = APIRouter()


class YouTubeSetupRequest(BaseModel):
    """Request body for setting up YouTube Music auth."""
    user_id: str
    headers: str


@router.post("/youtube/setup")
def setup_youtube_auth(request: YouTubeSetupRequest, db: Session = Depends(get_db)):
    """Store YouTube Music authentication credentials for a user.

    Accepts raw browser request headers that ytmusicapi uses for authentication.
    """
    return YouTubeMusicClient.setup_auth(db, request.user_id, request.headers)


@router.get("/youtube/status")
def get_youtube_auth_status(user_id: str = "demo_user", db: Session = Depends(get_db)):
    """Check whether a user has valid YouTube Music authentication."""
    return YouTubeMusicClient.check_auth_status(db, user_id)
