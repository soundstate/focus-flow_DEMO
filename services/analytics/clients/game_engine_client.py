"""HTTP client for the Game Engine service."""
import httpx
import logging
from typing import Optional

from analytics.config.settings import get_settings

logger = logging.getLogger(__name__)


class GameEngineClient:
    """Communicates with the Game Engine service over HTTP."""

    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.game_engine_url

    async def get_user_level(self, user_id: str) -> Optional[dict]:
        """Fetch level information for a user from the Game Engine.

        Args:
            user_id: The user identifier.

        Returns:
            Level dict or None on failure.
        """
        url = f"{self.base_url}/api/v1/levels/users/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch level for user %s: %s", user_id, exc)
            return None

    async def get_user_streak(self, user_id: str) -> Optional[dict]:
        """Fetch streak information for a user from the Game Engine.

        Args:
            user_id: The user identifier.

        Returns:
            Streak dict or None on failure.
        """
        url = f"{self.base_url}/api/v1/streaks/users/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch streak for user %s: %s", user_id, exc)
            return None
