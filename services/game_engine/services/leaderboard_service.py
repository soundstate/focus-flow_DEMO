"""Leaderboard service."""
from typing import List, Optional

from sqlalchemy.orm import Session

from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak


class LeaderboardService:
    """Provides XP and streak leaderboards backed by the database."""

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client

    async def get_xp_leaderboard(self, limit: int = 50) -> List[dict]:
        """Return the top users by total XP."""
        levels = (
            self.db.query(UserLevel)
            .order_by(UserLevel.total_xp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "user_id": l.user_id,
                "level": l.current_level,
                "total_xp": l.total_xp,
                "rank": i + 1,
            }
            for i, l in enumerate(levels)
        ]

    async def get_streak_leaderboard(self, limit: int = 50) -> List[dict]:
        """Return the top users by current streak."""
        streaks = (
            self.db.query(UserStreak)
            .order_by(UserStreak.current_streak.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "user_id": s.user_id,
                "current_streak": s.current_streak,
                "longest_streak": s.longest_streak,
                "rank": i + 1,
            }
            for i, s in enumerate(streaks)
        ]
