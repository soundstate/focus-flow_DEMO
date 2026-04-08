"""Correlation engine -- interprets analytics correlations with AI context."""

import json
import logging
import httpx
from typing import Optional

from sqlalchemy.orm import Session

from ai_insights.clients.openai_client import OpenAIClient
from ai_insights.config.ai_settings import get_settings

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """Fetches correlations from the Analytics service and interprets them with AI."""

    def __init__(self, db: Session, analytics_url: Optional[str] = None):
        self.db = db
        self.settings = get_settings()
        self.analytics_url = analytics_url or self.settings.analytics_url
        self.client = OpenAIClient(db)

    async def get_correlations(self, user_id: str) -> list:
        """Fetch raw correlations from the Analytics service.

        Args:
            user_id: User identifier.

        Returns:
            List of correlation dicts.
        """
        url = f"{self.analytics_url}/api/v1/correlations/users/{user_id}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch correlations for %s: %s", user_id, exc)
            return []

    def interpret_correlations(self, user_id: str, correlations: list) -> dict:
        """Use AI to interpret correlation data into actionable insights.

        Args:
            user_id: User identifier.
            correlations: List of correlation result dicts.

        Returns:
            Dict with interpreted insights.
        """
        if not correlations:
            return {
                "user_id": user_id,
                "interpretations": [],
                "summary": "Not enough data to interpret correlations yet.",
            }

        prompt = (
            "You are a productivity analyst. Interpret these statistical correlations "
            "from a user's focus session data and explain what they mean practically.\n\n"
            f"Correlations:\n{json.dumps(correlations, indent=2)}\n\n"
            "Provide your response as JSON with this structure:\n"
            '{"interpretations": [{"correlation_type": "...", "meaning": "...", '
            '"actionable_advice": "..."}], "summary": "Overall interpretation"}'
        )

        result = self.client.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="correlation_interpretation",
            ttl_seconds=self.settings.coaching_cache_ttl,
        )

        result["user_id"] = user_id
        return result
