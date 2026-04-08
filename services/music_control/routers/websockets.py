"""WebSocket bridge for real-time playback updates via Redis pub/sub."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
import logging

router = APIRouter()
logger = logging.getLogger("music_control.routers.websockets")


@router.websocket("/playback")
async def playback_ws(websocket: WebSocket, user_id: str = "demo_user"):
    """WebSocket endpoint that streams playback state changes to the client.

    Subscribes to the Redis 'music.track_changed' channel and forwards
    messages matching the connected user_id.
    """
    await websocket.accept()

    try:
        import redis.asyncio as aioredis
        from music_control.config.settings import get_settings

        settings = get_settings()
        redis_client = aioredis.from_url(settings.redis_url)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("music.track_changed")

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                raw_data = message["data"]
                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode("utf-8")
                data = json.loads(raw_data)
                if data.get("user_id") == user_id:
                    await websocket.send_json(data.get("payload", {}))
        except WebSocketDisconnect:
            pass
        finally:
            await pubsub.unsubscribe("music.track_changed")
            await redis_client.close()

    except ImportError:
        logger.warning("Redis not available for WebSocket bridge")
        try:
            await websocket.send_json({"error": "Redis not available"})
            await websocket.close()
        except Exception:
            pass
    except Exception:
        logger.exception("WebSocket error")
        try:
            await websocket.close()
        except Exception:
            pass
