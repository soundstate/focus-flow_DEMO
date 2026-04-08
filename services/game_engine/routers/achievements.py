"""Achievement router for the Game Engine API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.achievement_service import AchievementService

router = APIRouter()


@router.get("/users/{user_id}")
def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """Get all achievements for a user."""
    return AchievementService(db).get_user_achievements(user_id)


@router.get("/users/{user_id}/recent")
def get_recent(user_id: str, limit: int = 5, db: Session = Depends(get_db)):
    """Get recently unlocked achievements for a user."""
    all_ach = AchievementService(db).get_user_achievements(user_id)
    unlocked = [a for a in all_ach if a.is_unlocked]
    unlocked.sort(key=lambda a: a.unlocked_at or a.created_at, reverse=True)
    return unlocked[:limit]


@router.get("/users/{user_id}/stats")
def get_stats(user_id: str, db: Session = Depends(get_db)):
    """Get achievement statistics for a user."""
    return AchievementService(db).get_stats(user_id)
