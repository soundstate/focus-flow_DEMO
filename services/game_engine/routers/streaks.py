"""Streak router for the Game Engine API."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.streak_service import StreakService
from game_engine.calculators.streak_calculator import MAX_GAP_DAYS

router = APIRouter()


@router.get("/users/{user_id}")
def get_user_streak(user_id: str, db: Session = Depends(get_db)):
    """Get streak information for a user, including computed fields."""
    streak = StreakService(db).get_streak(user_id)
    if streak is None:
        raise HTTPException(status_code=404, detail="User streak not found")

    # compute is_active and days_until_break
    is_active = False
    days_until_break = 0
    if streak.last_session_date is not None:
        gap = (date.today() - streak.last_session_date).days
        is_active = gap <= MAX_GAP_DAYS
        days_until_break = max(0, MAX_GAP_DAYS - gap + 1) if is_active else 0

    return {
        "user_id": streak.user_id,
        "current_streak": streak.current_streak,
        "longest_streak": streak.longest_streak,
        "last_session_date": streak.last_session_date,
        "streak_start_date": streak.streak_start_date,
        "total_sessions": streak.total_sessions,
        "is_active": is_active,
        "days_until_break": days_until_break,
    }
