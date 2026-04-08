"""Tests for AI Insights event handlers."""

import pytest
from unittest.mock import MagicMock

from ai_insights.events.handlers import handle_session_completed


@pytest.mark.asyncio
async def test_handle_session_completed_logs_event():
    """handler logs session data without calling OpenAI."""
    data = {
        "user_id": "user_1",
        "duration": 25,
        "productivity_score": 0.85,
        "xp_earned": 100,
    }
    db = MagicMock()
    # Should not raise
    await handle_session_completed(data, db)


@pytest.mark.asyncio
async def test_handle_session_completed_missing_user_id():
    """handler skips events without user_id."""
    data = {"duration": 25}
    db = MagicMock()
    # Should not raise, just warn
    await handle_session_completed(data, db)


@pytest.mark.asyncio
async def test_handle_session_completed_empty_data():
    """handler handles empty event payload."""
    data = {}
    db = MagicMock()
    await handle_session_completed(data, db)
