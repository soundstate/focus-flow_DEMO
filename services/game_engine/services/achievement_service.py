"""Achievement evaluation and management service."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from game_engine.models.achievement_models import (
    Achievement,
    AchievementType,
    AchievementCategory,
)

# Achievement definitions: type -> (title, description, icon, category, progress_required)
ACHIEVEMENT_DEFS = {
    AchievementType.FIRST_SESSION: (
        "First Focus",
        "Complete your first focus session",
        "rocket",
        AchievementCategory.MILESTONE,
        1,
    ),
    AchievementType.STREAK_3: (
        "Hat Trick",
        "Maintain a 3-day focus streak",
        "fire",
        AchievementCategory.STREAK,
        3,
    ),
    AchievementType.STREAK_7: (
        "Week Warrior",
        "Maintain a 7-day focus streak",
        "calendar",
        AchievementCategory.STREAK,
        7,
    ),
    AchievementType.STREAK_30: (
        "Monthly Master",
        "Maintain a 30-day focus streak",
        "crown",
        AchievementCategory.STREAK,
        30,
    ),
    AchievementType.STREAK_100: (
        "Century Club",
        "Maintain a 100-day focus streak",
        "trophy",
        AchievementCategory.STREAK,
        100,
    ),
    AchievementType.TOTAL_SESSIONS_10: (
        "Getting Started",
        "Complete 10 focus sessions",
        "star",
        AchievementCategory.CONSISTENCY,
        10,
    ),
    AchievementType.TOTAL_SESSIONS_50: (
        "Dedicated",
        "Complete 50 focus sessions",
        "medal",
        AchievementCategory.CONSISTENCY,
        50,
    ),
    AchievementType.TOTAL_SESSIONS_100: (
        "Centurion",
        "Complete 100 focus sessions",
        "shield",
        AchievementCategory.CONSISTENCY,
        100,
    ),
    AchievementType.DEEP_WORK_MASTER: (
        "Deep Work Master",
        "Complete a 90+ minute uninterrupted session",
        "brain",
        AchievementCategory.MASTERY,
        1,
    ),
    AchievementType.EARLY_BIRD: (
        "Early Bird",
        "Complete a session before 7 AM",
        "sun",
        AchievementCategory.TIME_BASED,
        1,
    ),
    AchievementType.NIGHT_OWL: (
        "Night Owl",
        "Complete a session after 11 PM",
        "moon",
        AchievementCategory.TIME_BASED,
        1,
    ),
}

# Mapping from achievement type to the session_data key and threshold used for progress
_PROGRESS_KEYS = {
    AchievementType.FIRST_SESSION: ("total_sessions", 1),
    AchievementType.STREAK_3: ("current_streak", 3),
    AchievementType.STREAK_7: ("current_streak", 7),
    AchievementType.STREAK_30: ("current_streak", 30),
    AchievementType.STREAK_100: ("current_streak", 100),
    AchievementType.TOTAL_SESSIONS_10: ("total_sessions", 10),
    AchievementType.TOTAL_SESSIONS_50: ("total_sessions", 50),
    AchievementType.TOTAL_SESSIONS_100: ("total_sessions", 100),
    AchievementType.DEEP_WORK_MASTER: ("deep_work_minutes", 90),
    AchievementType.EARLY_BIRD: ("early_bird", 1),
    AchievementType.NIGHT_OWL: ("night_owl", 1),
}


class AchievementService:
    """Evaluates session data against achievement requirements and unlocks them."""

    def __init__(self, db: Session):
        self.db = db

    def _ensure_achievements_exist(self, user_id: str) -> None:
        """Create achievement rows for all types if the user has none."""
        existing = (
            self.db.query(Achievement).filter_by(user_id=user_id).count()
        )
        if existing > 0:
            return

        for ach_type, (title, description, icon, category, progress_required) in ACHIEVEMENT_DEFS.items():
            self.db.add(
                Achievement(
                    user_id=user_id,
                    achievement_type=ach_type,
                    category=category,
                    title=title,
                    description=description,
                    icon=icon,
                    progress_required=progress_required,
                    progress_current=0,
                    is_unlocked=False,
                )
            )
        self.db.commit()

    def evaluate(self, user_id: str, session_data: dict) -> List[Achievement]:
        """Evaluate session data and unlock any qualifying achievements.

        Args:
            user_id: The user to evaluate.
            session_data: Dict with keys like total_sessions, current_streak,
                          session_completed, deep_work_minutes, early_bird, night_owl.

        Returns:
            List of newly unlocked Achievement objects.
        """
        self._ensure_achievements_exist(user_id)

        achievements = (
            self.db.query(Achievement)
            .filter_by(user_id=user_id, is_unlocked=False)
            .all()
        )

        newly_unlocked: List[Achievement] = []

        for ach in achievements:
            progress_info = _PROGRESS_KEYS.get(ach.achievement_type)
            if progress_info is None:
                continue

            data_key, threshold = progress_info
            current_value = session_data.get(data_key, 0)

            # update progress
            ach.progress_current = min(current_value, ach.progress_required)

            if current_value >= threshold:
                ach.is_unlocked = True
                ach.unlocked_at = datetime.utcnow()
                ach.progress_current = ach.progress_required
                newly_unlocked.append(ach)

        self.db.commit()
        return newly_unlocked

    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """Get all achievements for a user."""
        self._ensure_achievements_exist(user_id)
        return (
            self.db.query(Achievement)
            .filter_by(user_id=user_id)
            .all()
        )

    def get_stats(self, user_id: str) -> dict:
        """Get achievement statistics for a user."""
        achievements = self.get_user_achievements(user_id)
        total = len(achievements)
        unlocked = [a for a in achievements if a.is_unlocked]
        total_unlocked = len(unlocked)

        by_category: dict = {}
        for ach in achievements:
            cat = ach.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "unlocked": 0}
            by_category[cat]["total"] += 1
            if ach.is_unlocked:
                by_category[cat]["unlocked"] += 1

        return {
            "user_id": user_id,
            "total_unlocked": total_unlocked,
            "total_available": total,
            "completion_percentage": round(
                (total_unlocked / total * 100) if total > 0 else 0, 1
            ),
            "recent_unlocks": sorted(
                unlocked,
                key=lambda a: a.unlocked_at or a.created_at,
                reverse=True,
            )[:5],
            "by_category": by_category,
        }
