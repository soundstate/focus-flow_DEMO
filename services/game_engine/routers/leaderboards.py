"""Leaderboard router for the Game Engine API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.leaderboard_service import LeaderboardService

router = APIRouter()


@router.get("/")
async def get_xp_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Get the XP leaderboard."""
    return await LeaderboardService(db).get_xp_leaderboard(limit=limit)


@router.get("/streaks")
async def get_streak_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Get the streak leaderboard."""
    return await LeaderboardService(db).get_streak_leaderboard(limit=limit)
