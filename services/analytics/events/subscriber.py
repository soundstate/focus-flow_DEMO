"""Redis pub/sub subscriber for Analytics service.

Listens for events from other services (Focus Engine, Game Engine) and
dispatches them to the appropriate handler.
"""
import json
import logging
import asyncio

from analytics.events.handlers import (
    handle_session_completed,
    handle_achievement_unlocked,
    handle_level_up,
)

logger = logging.getLogger("analytics.events.subscriber")

# Map event types to handler functions
EVENT_HANDLERS = {
    "session.completed": handle_session_completed,
    "achievement.unlocked": handle_achievement_unlocked,
    "level.up": handle_level_up,
}


async def start_subscriber(redis_client, db_session_factory, publisher=None):
    """Subscribe to relevant Redis channels and dispatch events.

    Args:
        redis_client: An async Redis client instance.
        db_session_factory: A callable that returns a new SQLAlchemy Session.
        publisher: Optional EventPublisher for outgoing events.
    """
    channels = list(EVENT_HANDLERS.keys())
    logger.info("Subscribing to channels: %s", channels)

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(*channels)

    logger.info("Analytics subscriber started, listening for events...")

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode("utf-8")

            handler = EVENT_HANDLERS.get(channel)
            if handler is None:
                logger.warning("No handler for channel: %s", channel)
                continue

            try:
                raw_data = message["data"]
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode("utf-8")
                data = json.loads(raw_data)
                payload = {
                    **data.get("payload", {}),
                    "user_id": data.get("user_id"),
                    "event_type": data.get("event_type"),
                }

                db = db_session_factory()
                try:
                    await handler(payload, db, publisher)
                finally:
                    db.close()

            except Exception:
                logger.exception(
                    "Error handling event on channel %s", channel
                )
    except asyncio.CancelledError:
        logger.info("Subscriber task cancelled, shutting down...")
    finally:
        await pubsub.unsubscribe(*channels)
        await pubsub.close()
        logger.info("Subscriber stopped.")
