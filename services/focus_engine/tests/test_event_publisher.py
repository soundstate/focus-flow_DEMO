"""Tests for Redis event publisher."""
import pytest
import json
from unittest.mock import AsyncMock
from datetime import datetime


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.publish = AsyncMock(return_value=1)
    return redis


@pytest.mark.asyncio
async def test_publish_event_sends_to_redis(mock_redis):
    from events.publisher import EventPublisher
    publisher = EventPublisher(redis_client=mock_redis)
    await publisher.publish(
        event_type="session.completed",
        user_id="user_123",
        payload={"session_id": "sess_1", "actual_duration": 25},
    )
    mock_redis.publish.assert_called_once()
    call_args = mock_redis.publish.call_args
    channel = call_args[0][0]
    message = json.loads(call_args[0][1])
    assert channel == "session.completed"
    assert message["event_type"] == "session.completed"
    assert message["source_service"] == "focus_engine"
    assert message["user_id"] == "user_123"
    assert message["payload"]["session_id"] == "sess_1"
    assert "timestamp" in message


@pytest.mark.asyncio
async def test_publish_event_includes_timestamp(mock_redis):
    from events.publisher import EventPublisher
    publisher = EventPublisher(redis_client=mock_redis)
    await publisher.publish(event_type="session.started", user_id="user_123", payload={})
    message = json.loads(mock_redis.publish.call_args[0][1])
    datetime.fromisoformat(message["timestamp"])
