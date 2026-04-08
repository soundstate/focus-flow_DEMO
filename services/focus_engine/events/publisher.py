"""Redis pub/sub event publisher."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("focus_engine.events.publisher")
SERVICE_NAME = "focus_engine"


class EventPublisher:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event_type: str, user_id: str, payload: dict) -> None:
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_service": SERVICE_NAME,
            "user_id": user_id,
            "payload": payload,
        }
        await self.redis.publish(event_type, json.dumps(message))
        logger.info("Published %s for user %s", event_type, user_id)
