"""Streak tracking service."""
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from game_engine.models.streak_models import UserStreak
from game_engine.calculators.streak_calculator import StreakCalculator


class StreakService:
    """Manages user streak tracking and updates."""

    def __init__(self, db: Session):
        self.db = db

    def update(self, user_id: str) -> dict:
        """Update streak for a user after a session.

        Returns the StreakCalculator result dict (new_streak, is_broken, is_milestone, milestone_type).
        """
        streak = self.db.query(UserStreak).filter_by(user_id=user_id).first()
        if streak is None:
            streak = UserStreak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                total_sessions=0,
            )
            self.db.add(streak)
            self.db.flush()

        result = StreakCalculator.update_streak(
            streak.last_session_date, streak.current_streak
        )

        streak.current_streak = result["new_streak"]
        streak.last_session_date = date.today()
        streak.total_sessions += 1

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        if result["is_broken"]:
            streak.streak_start_date = date.today()
        elif streak.streak_start_date is None:
            streak.streak_start_date = date.today()

        self.db.commit()
        return result

    def get_streak(self, user_id: str) -> Optional[UserStreak]:
        """Get the streak record for a user, or None if not found."""
        return self.db.query(UserStreak).filter_by(user_id=user_id).first()
