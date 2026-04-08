"""Tests for Music Control event handlers."""

import pytest
from unittest.mock import MagicMock

from music_control.events.handlers import (
    handle_session_started,
    handle_session_completed,
    handle_session_paused,
    handle_session_resumed,
)


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.mark.asyncio
async def test_handle_session_started(mock_db):
    data = {"user_id": "user_1", "session_id": "s1"}
    # Should not raise
    await handle_session_started(data, mock_db)


@pytest.mark.asyncio
async def test_handle_session_completed(mock_db):
    data = {"user_id": "user_1", "duration": 25, "productivity_score": 0.85}
    await handle_session_completed(data, mock_db)


@pytest.mark.asyncio
async def test_handle_session_paused(mock_db):
    data = {"user_id": "user_1"}
    await handle_session_paused(data, mock_db)


@pytest.mark.asyncio
async def test_handle_session_resumed(mock_db):
    data = {"user_id": "user_1"}
    await handle_session_resumed(data, mock_db)


@pytest.mark.asyncio
async def test_handle_session_started_missing_user(mock_db):
    data = {}
    # Should handle gracefully (uses "unknown" default)
    await handle_session_started(data, mock_db)


@pytest.mark.asyncio
async def test_handle_session_completed_missing_fields(mock_db):
    data = {}
    await handle_session_completed(data, mock_db)
