"""Streak calculation logic with grace period."""
from datetime import date
from typing import Optional

MILESTONE_DAYS = {3: "3_day", 7: "7_day", 30: "30_day", 100: "100_day"}
MAX_GAP_DAYS = 2


class StreakCalculator:
    @staticmethod
    def update_streak(
        last_session_date: Optional[date], current_streak: int
    ) -> dict:
        today = date.today()

        if last_session_date is None:
            new_streak, is_broken = 1, False
        elif last_session_date == today:
            new_streak, is_broken = current_streak, False
        else:
            gap = (today - last_session_date).days
            if gap <= MAX_GAP_DAYS:
                new_streak, is_broken = current_streak + 1, False
            else:
                new_streak, is_broken = 1, True

        milestone_type = MILESTONE_DAYS.get(new_streak)
        return {
            "new_streak": new_streak,
            "is_broken": is_broken,
            "is_milestone": milestone_type is not None,
            "milestone_type": milestone_type,
        }
