"""Event handlers for incoming events consumed by Music Control service."""
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger("music_control.events.handlers")


async def handle_session_started(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.started event from the Focus Engine.

    Logs the event. Could trigger auto-play in the future.

    Args:
        data: Event payload with user_id, session_id, etc.
        db: SQLAlchemy session.
        publisher: Optional EventPublisher for outgoing events.
    """
    user_id = data.get("user_id", "unknown")
    session_id = data.get("session_id", "unknown")
    logger.info(
        "Session started for user %s (session %s) -- auto-play could trigger here",
        user_id,
        session_id,
    )


async def handle_session_completed(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.completed event from the Focus Engine.

    Logs the event. Could update track effectiveness in the future.

    Args:
        data: Event payload with user_id, duration, productivity_score, etc.
        db: SQLAlchemy session.
        publisher: Optional EventPublisher.
    """
    user_id = data.get("user_id", "unknown")
    duration = data.get("duration", 0)
    score = data.get("productivity_score", 0.0)
    logger.info(
        "Session completed for user %s: duration=%s min, score=%.2f",
        user_id,
        duration,
        score,
    )


async def handle_session_paused(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.paused event from the Focus Engine.

    Logs the event. Could pause music playback in the future.

    Args:
        data: Event payload with user_id, session_id, etc.
        db: SQLAlchemy session.
        publisher: Optional EventPublisher.
    """
    user_id = data.get("user_id", "unknown")
    logger.info("Session paused for user %s -- could pause playback", user_id)


async def handle_session_resumed(data: dict, db: Session, publisher=None) -> None:
    """Handle a session.resumed event from the Focus Engine.

    Logs the event. Could resume music playback in the future.

    Args:
        data: Event payload with user_id, session_id, etc.
        db: SQLAlchemy session.
        publisher: Optional EventPublisher.
    """
    user_id = data.get("user_id", "unknown")
    logger.info("Session resumed for user %s -- could resume playback", user_id)
