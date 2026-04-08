"""Level and XP management service."""
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from game_engine.models.level_models import UserLevel, calculate_xp_for_level
from game_engine.models.xp_history_models import XPHistory


class LevelService:
    """Manages user levels, XP awards, and level-up progression."""

    def __init__(self, db: Session):
        self.db = db

    def award_xp(
        self,
        user_id: str,
        session_id: str,
        base_xp: int,
        bonus_xp: int,
        total_xp: int,
        reason: str,
    ) -> dict:
        """Award XP to a user, creating their level record if needed.

        Returns dict with level_up, new_level, total_xp, current_xp, xp_to_next_level.
        """
        level = self.db.query(UserLevel).filter_by(user_id=user_id).first()
        if level is None:
            level = UserLevel(
                user_id=user_id,
                current_level=1,
                current_xp=0,
                total_xp=0,
                xp_to_next_level=calculate_xp_for_level(2),
            )
            self.db.add(level)
            self.db.flush()

        # record XP history
        self.db.add(
            XPHistory(
                user_id=user_id,
                session_id=session_id,
                base_xp=base_xp,
                bonus_xp=bonus_xp,
                total_xp=total_xp,
                reason=reason,
            )
        )

        # apply XP
        level.current_xp += total_xp
        level.total_xp += total_xp

        # check for level-ups
        leveled_up = False
        while level.current_xp >= level.xp_to_next_level:
            level.current_xp -= level.xp_to_next_level
            level.current_level += 1
            level.xp_to_next_level = calculate_xp_for_level(level.current_level + 1)
            leveled_up = True
            level.level_up_at = datetime.utcnow()

        self.db.commit()

        return {
            "level_up": leveled_up,
            "new_level": level.current_level,
            "total_xp": level.total_xp,
            "current_xp": level.current_xp,
            "xp_to_next_level": level.xp_to_next_level,
        }

    def get_user_level(self, user_id: str) -> Optional[UserLevel]:
        """Get the level record for a user, or None if not found."""
        return self.db.query(UserLevel).filter_by(user_id=user_id).first()

    def get_xp_history(self, user_id: str, limit: int = 20) -> List[XPHistory]:
        """Get recent XP history for a user."""
        return (
            self.db.query(XPHistory)
            .filter_by(user_id=user_id)
            .order_by(XPHistory.created_at.desc())
            .limit(limit)
            .all()
        )
