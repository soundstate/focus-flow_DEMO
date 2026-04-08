"""Event handlers for incoming events consumed by AI Insights service."""
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("ai_insights.events.handlers")


async def handle_session_completed(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.completed event from the Focus Engine.

    Logs the event for awareness. Does NOT trigger an OpenAI call per event
    to avoid excessive API usage. Coaching insights are generated on-demand
    via the REST endpoints instead.

    Args:
        data: Event payload with user_id, duration, productivity_score, etc.
        db: SQLAlchemy session.
        publisher: Unused, kept for handler signature consistency.
    """
    user_id = data.get("user_id")
    if not user_id:
        logger.warning("session.completed event missing user_id, skipping")
        return

    duration = data.get("duration", 0)
    score = data.get("productivity_score", 0.0)
    logger.info(
        "Session completed for user %s: duration=%s min, score=%.2f "
        "(insight generation deferred to on-demand endpoints)",
        user_id,
        duration,
        score,
    )
