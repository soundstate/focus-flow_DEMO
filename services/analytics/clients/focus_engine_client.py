"""HTTP client for the Focus Engine service."""
import httpx
import logging
from typing import List, Optional

from analytics.config.settings import get_settings

logger = logging.getLogger(__name__)


class FocusEngineClient:
    """Communicates with the Focus Engine service over HTTP."""

    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.focus_engine_url

    async def get_user_sessions(self, user_id: str) -> List[dict]:
        """Fetch all sessions for a user from the Focus Engine.

        Args:
            user_id: The user identifier.

        Returns:
            List of session dicts, or empty list on failure.
        """
        url = f"{self.base_url}/api/v1/sessions/user/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch sessions for user %s: %s", user_id, exc)
            return []
