"""Session analyzer -- fetches user context from Focus Engine."""

import httpx
import logging
from typing import Optional

from ai_insights.config.ai_settings import get_settings

logger = logging.getLogger(__name__)


class SessionAnalyzer:
    """Fetches and prepares user session data for AI analysis."""

    def __init__(self, base_url: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.focus_engine_url

    async def get_user_context(self, user_id: str) -> dict:
        """Fetch user session history from the Focus Engine.

        Args:
            user_id: The user identifier.

        Returns:
            Dict with session data, or empty context on failure.
        """
        url = f"{self.base_url}/api/v1/sessions/user/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                sessions = response.json()

            # Summarise the context
            total_sessions = len(sessions)
            total_minutes = sum(s.get("duration", 0) for s in sessions)
            avg_productivity = 0.0
            if total_sessions > 0:
                scores = [s.get("productivity_score", 0.0) for s in sessions]
                avg_productivity = sum(scores) / total_sessions

            return {
                "user_id": user_id,
                "total_sessions": total_sessions,
                "total_focus_minutes": total_minutes,
                "avg_productivity_score": round(avg_productivity, 2),
                "recent_sessions": sessions[-5:] if sessions else [],
            }
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch user context for %s: %s", user_id, exc)
            return {
                "user_id": user_id,
                "total_sessions": 0,
                "total_focus_minutes": 0,
                "avg_productivity_score": 0.0,
                "recent_sessions": [],
            }
