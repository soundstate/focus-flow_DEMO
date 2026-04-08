"""Redis pub/sub event publisher for Game Engine."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("game_engine.events.publisher")
SERVICE_NAME = "game_engine"


class EventPublisher:
    """Publishes game engine events to Redis pub/sub channels."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event_type: str, user_id: str, payload: dict) -> None:
        """Publish an event to the specified channel.

        Args:
            event_type: The event channel name (e.g. 'achievement.unlocked', 'level.up').
            user_id: The user this event pertains to.
            payload: Event-specific data.
        """
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_service": SERVICE_NAME,
            "user_id": user_id,
            "payload": payload,
        }
        await self.redis.publish(event_type, json.dumps(message))
        logger.info("Published %s for user %s", event_type, user_id)
