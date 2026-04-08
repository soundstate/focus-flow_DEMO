"""Event handlers for incoming events consumed by Analytics service."""
import logging
from sqlalchemy.orm import Session

from analytics.services.metrics_calculator import MetricsCalculator

logger = logging.getLogger("analytics.events.handlers")


async def handle_session_completed(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.completed event from the Focus Engine.

    Updates the daily aggregate for the user with session data.

    Args:
        data: Event payload with user_id, duration, productivity_score, xp_earned, etc.
        db: SQLAlchemy session.
        publisher: Unused, kept for handler signature consistency.
    """
    user_id = data.get("user_id")
    if not user_id:
        logger.warning("session.completed event missing user_id, skipping")
        return

    session_data = {
        "duration": data.get("duration", 25),
        "productivity_score": data.get("productivity_score", 0.0),
        "xp_earned": data.get("xp_earned", 0),
        "interruptions": data.get("interruptions", 0),
    }

    calc = MetricsCalculator(db)
    calc.update_daily_aggregate(user_id, session_data)
    logger.info("Updated daily aggregate for user %s from session.completed event", user_id)


async def handle_achievement_unlocked(data: dict, db: Session, publisher=None) -> None:
    """Handle an achievement.unlocked event from the Game Engine.

    Currently logs the event for future analytics processing.

    Args:
        data: Event payload with user_id, achievement_type, etc.
        db: SQLAlchemy session.
        publisher: Unused.
    """
    user_id = data.get("user_id", "unknown")
    achievement = data.get("achievement_type", "unknown")
    logger.info("Achievement unlocked for user %s: %s", user_id, achievement)


async def handle_level_up(data: dict, db: Session, publisher=None) -> None:
    """Handle a level.up event from the Game Engine.

    Currently logs the event for future analytics processing.

    Args:
        data: Event payload with user_id, new_level, etc.
        db: SQLAlchemy session.
        publisher: Unused.
    """
    user_id = data.get("user_id", "unknown")
    new_level = data.get("new_level", "unknown")
    logger.info("Level up for user %s: reached level %s", user_id, new_level)
