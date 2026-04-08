"""Effectiveness router for music productivity reports."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from music_control.database.connection import get_db
from music_control.services.effectiveness_tracker import EffectivenessTracker

router = APIRouter()


@router.get("/users/{user_id}")
def get_effectiveness_report(user_id: str, db: Session = Depends(get_db)):
    """Get overall music effectiveness report for a user."""
    tracker = EffectivenessTracker(db)
    return tracker.get_report(user_id)


@router.get("/users/{user_id}/tracks")
def get_track_effectiveness(
    user_id: str,
    track_id: str = "",
    db: Session = Depends(get_db),
):
    """Get effectiveness data for a specific track.

    Query params:
        track_id: The track to look up (required).
    """
    if not track_id:
        return {"error": "track_id query parameter is required"}
    tracker = EffectivenessTracker(db)
    return tracker.get_track_report(user_id, track_id)
