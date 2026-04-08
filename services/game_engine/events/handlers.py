"""Event handlers for incoming events consumed by Game Engine."""
import logging
from sqlalchemy.orm import Session

from game_engine.services.streak_service import StreakService
from game_engine.services.level_service import LevelService
from game_engine.services.achievement_service import AchievementService
from game_engine.calculators.experience_calculator import ExperienceCalculator

logger = logging.getLogger("game_engine.events.handlers")


async def handle_session_completed(
    data: dict, db: Session, publisher=None
) -> dict:
    """Handle a session.completed event from the Focus Engine.

    Pipeline:
      1. Update streak
      2. Calculate XP (using updated streak)
      3. Award XP
      4. Evaluate achievements
      5. Publish achievement.unlocked and level.up events if applicable

    Args:
        data: The event payload with user_id, session_id, duration, completed, etc.
        db: SQLAlchemy session.
        publisher: Optional EventPublisher for outgoing events.

    Returns:
        Summary dict of all gamification results.
    """
    user_id = data.get("user_id")
    session_id = data.get("session_id", "unknown")
    duration = data.get("duration", 25)
    completed = data.get("completed", True)
    productivity_score = data.get("productivity_score")

    logger.info(
        "Processing session.completed for user %s, session %s",
        user_id,
        session_id,
    )

    # 1. update streak
    streak_svc = StreakService(db)
    streak_result = streak_svc.update(user_id)
    streak = streak_svc.get_streak(user_id)
    current_streak = streak.current_streak if streak else 0

    # 2. calculate XP
    xp_result = ExperienceCalculator.calculate(
        session_duration=duration,
        session_completed=completed,
        productivity_score=productivity_score,
        current_streak=current_streak,
    )

    # 3. award XP
    level_svc = LevelService(db)
    level_result = level_svc.award_xp(
        user_id=user_id,
        session_id=session_id,
        base_xp=xp_result["base_xp"],
        bonus_xp=xp_result["bonus_xp"],
        total_xp=xp_result["total_xp"],
        reason=xp_result["reason"],
    )

    # 4. evaluate achievements
    ach_svc = AchievementService(db)
    session_data = {
        "total_sessions": streak.total_sessions if streak else 1,
        "current_streak": current_streak,
        "session_completed": completed,
    }
    newly_unlocked = ach_svc.evaluate(user_id, session_data)

    # 5. publish outgoing events
    if publisher is not None:
        for ach in newly_unlocked:
            await publisher.publish(
                "achievement.unlocked",
                user_id,
                {
                    "achievement_type": ach.achievement_type.value
                    if hasattr(ach.achievement_type, "value")
                    else str(ach.achievement_type),
                    "title": ach.title,
                    "description": ach.description,
                    "icon": ach.icon,
                },
            )

        if level_result.get("level_up"):
            await publisher.publish(
                "level.up",
                user_id,
                {
                    "new_level": level_result["new_level"],
                    "total_xp": level_result["total_xp"],
                },
            )

    summary = {
        "streak": streak_result,
        "xp": xp_result,
        "level": level_result,
        "achievements_unlocked": len(newly_unlocked),
    }
    logger.info("Session processing complete for user %s: %s", user_id, summary)
    return summary
