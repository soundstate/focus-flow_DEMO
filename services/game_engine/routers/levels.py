"""Level and XP router for the Game Engine API."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.level_service import LevelService
from game_engine.services.streak_service import StreakService
from game_engine.services.achievement_service import AchievementService
from game_engine.calculators.experience_calculator import ExperienceCalculator

router = APIRouter()


class ProcessSessionRequest(BaseModel):
    """Request body for manual session processing."""
    user_id: str
    session_id: str
    session_duration: int
    session_completed: bool = True
    productivity_score: Optional[float] = None


@router.get("/users/{user_id}")
def get_user_level(user_id: str, db: Session = Depends(get_db)):
    """Get the level and XP information for a user."""
    level = LevelService(db).get_user_level(user_id)
    if level is None:
        raise HTTPException(status_code=404, detail="User level not found")
    return {
        "user_id": level.user_id,
        "current_level": level.current_level,
        "current_xp": level.current_xp,
        "total_xp": level.total_xp,
        "xp_to_next_level": level.xp_to_next_level,
        "progress_percentage": round(
            (level.current_xp / level.xp_to_next_level * 100)
            if level.xp_to_next_level > 0
            else 0,
            1,
        ),
        "level_up_at": level.level_up_at,
    }


@router.get("/users/{user_id}/history")
def get_xp_history(
    user_id: str, limit: int = 20, db: Session = Depends(get_db)
):
    """Get XP history for a user."""
    return LevelService(db).get_xp_history(user_id, limit=limit)


@router.post("/process-session")
def process_session(request: ProcessSessionRequest, db: Session = Depends(get_db)):
    """Manual testing endpoint: process a session through the full gamification pipeline.

    Calculates XP, updates streak, awards XP, and evaluates achievements.
    """
    # 1. update streak
    streak_svc = StreakService(db)
    streak_result = streak_svc.update(request.user_id)
    streak = streak_svc.get_streak(request.user_id)

    # 2. calculate XP (uses updated streak)
    xp_result = ExperienceCalculator.calculate(
        session_duration=request.session_duration,
        session_completed=request.session_completed,
        productivity_score=request.productivity_score,
        current_streak=streak.current_streak if streak else 0,
    )

    # 3. award XP
    level_svc = LevelService(db)
    level_result = level_svc.award_xp(
        user_id=request.user_id,
        session_id=request.session_id,
        base_xp=xp_result["base_xp"],
        bonus_xp=xp_result["bonus_xp"],
        total_xp=xp_result["total_xp"],
        reason=xp_result["reason"],
    )

    # 4. evaluate achievements
    ach_svc = AchievementService(db)
    session_data = {
        "total_sessions": streak.total_sessions if streak else 1,
        "current_streak": streak.current_streak if streak else 1,
        "session_completed": request.session_completed,
    }
    newly_unlocked = ach_svc.evaluate(request.user_id, session_data)

    return {
        "streak": streak_result,
        "xp": xp_result,
        "level": level_result,
        "achievements_unlocked": [
            {
                "achievement_type": a.achievement_type,
                "title": a.title,
                "description": a.description,
            }
            for a in newly_unlocked
        ],
    }
