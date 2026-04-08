"""Tests for SessionService event publishing on state transitions."""

import sys
import types
import uuid
import sqlite3
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine, event, JSON, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from datetime import datetime, timedelta
import importlib

# Register SQLite adapter/converter for UUID objects so that
# uuid.uuid4() defaults in the ORM model work with SQLite.
sqlite3.register_adapter(uuid.UUID, lambda u: str(u))
sqlite3.register_converter("UUID", lambda b: uuid.UUID(b.decode()))

# ---------------------------------------------------------------------------
# Bootstrap: patch PostgreSQL-only types and modules *before* importing
# production code, following the same pattern as test_session_model.py.
# ---------------------------------------------------------------------------

import sqlalchemy.dialects.postgresql as _pg


class _FakeUUID(String):
    """Drop-in for postgresql.UUID that works on SQLite."""
    def __init__(self, as_uuid=False, **kw):
        super().__init__(length=36)


_pg.UUID = _FakeUUID
_pg.ARRAY = lambda *a, **kw: JSON()


class _TestBase(DeclarativeBase):
    pass


# Mock database.connection
_test_base_module = MagicMock()
_test_base_module.Base = _TestBase
_test_base_module.get_database = MagicMock()
_test_base_module.get_db = MagicMock()

# Mock config.settings
_test_settings_module = MagicMock()
_test_settings_module.get_settings = MagicMock(return_value=MagicMock(
    database_url="sqlite:///:memory:", debug_mode=False
))

sys.modules.setdefault("database", MagicMock())
sys.modules["database.connection"] = _test_base_module
sys.modules.setdefault("config", MagicMock())
sys.modules["config.settings"] = _test_settings_module

# Import the model first (bare import, works with pythonpath)
from models.session_models import FocusSession  # noqa: E402

# Create a mock for the broadcast function (from routers.websockets)
_mock_broadcast = AsyncMock()

# Build fake package hierarchy so that session_service.py's relative imports work.
# session_service.py lives at services/focus_engine/services/session_service.py
# It does:
#   from ..models.session_models import FocusSession
#   from ..routers.websockets import broadcast_session_update
#   from ..events.publisher import EventPublisher  (after our changes)
#
# For these relative imports to resolve, we need the parent package
# structure in sys.modules.

# Create the focus_engine package namespace
_fe_pkg = types.ModuleType("focus_engine")
_fe_pkg.__path__ = []
_fe_pkg.__package__ = "focus_engine"

# models sub-package
_fe_models = types.ModuleType("focus_engine.models")
_fe_models.__path__ = []
_fe_models.__package__ = "focus_engine.models"

_fe_models_session = types.ModuleType("focus_engine.models.session_models")
_fe_models_session.FocusSession = FocusSession
_fe_models.session_models = _fe_models_session

# routers sub-package
_fe_routers = types.ModuleType("focus_engine.routers")
_fe_routers.__path__ = []
_fe_routers.__package__ = "focus_engine.routers"

_fe_routers_ws = types.ModuleType("focus_engine.routers.websockets")
_fe_routers_ws.broadcast_session_update = _mock_broadcast
_fe_routers.websockets = _fe_routers_ws

# events sub-package (import the real publisher)
from events.publisher import EventPublisher  # noqa: E402

_fe_events = types.ModuleType("focus_engine.events")
_fe_events.__path__ = []
_fe_events.__package__ = "focus_engine.events"

_fe_events_publisher = types.ModuleType("focus_engine.events.publisher")
_fe_events_publisher.EventPublisher = EventPublisher
_fe_events.publisher = _fe_events_publisher

# services sub-package
_fe_services = types.ModuleType("focus_engine.services")
_fe_services.__path__ = []
_fe_services.__package__ = "focus_engine.services"

# Wire everything into sys.modules
sys.modules["focus_engine"] = _fe_pkg
sys.modules["focus_engine.models"] = _fe_models
sys.modules["focus_engine.models.session_models"] = _fe_models_session
sys.modules["focus_engine.routers"] = _fe_routers
sys.modules["focus_engine.routers.websockets"] = _fe_routers_ws
sys.modules["focus_engine.events"] = _fe_events
sys.modules["focus_engine.events.publisher"] = _fe_events_publisher
sys.modules["focus_engine.services"] = _fe_services

# Now import session_service using importlib so it resolves relative imports
# against the focus_engine package we just built.
import os as _os
_ss_path = _os.path.normpath(
    _os.path.join(_os.path.dirname(__file__), "..", "services", "session_service.py")
)
_spec = importlib.util.spec_from_file_location(
    "focus_engine.services.session_service", _ss_path,
    submodule_search_locations=[]
)
_ss_mod = importlib.util.module_from_spec(_spec)
_ss_mod.__package__ = "focus_engine.services"
sys.modules["focus_engine.services.session_service"] = _ss_mod
_spec.loader.exec_module(_ss_mod)

SessionService = _ss_mod.SessionService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session():
    """Create an in-memory SQLite session for testing."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(test_engine, "connect")
    def _pragma(dbapi_conn, _rec):
        dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")

    # Use FocusSession's own metadata so the table is created even when
    # another test module registered the model against a different Base.
    FocusSession.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture
def mock_publisher():
    """Create a mock EventPublisher."""
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture(autouse=True)
def wire_publisher(mock_publisher):
    """Wire mock publisher into SessionService for every test."""
    SessionService.set_publisher(mock_publisher)
    yield
    SessionService.set_publisher(None)


@pytest.fixture(autouse=True)
def reset_broadcast():
    """Reset the broadcast mock before each test."""
    _mock_broadcast.reset_mock()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_start_session_publishes_event(db_session, mock_publisher):
    session = await SessionService.start_session(
        db=db_session, user_id="user_42", duration_minutes=25, session_type="pomodoro"
    )
    mock_publisher.publish.assert_called_once()
    call_kwargs = mock_publisher.publish.call_args[1]
    assert call_kwargs["event_type"] == "session.started"
    assert call_kwargs["user_id"] == "user_42"


@pytest.mark.asyncio
async def test_complete_session_publishes_event(db_session, mock_publisher):
    # Start a session first
    session = await SessionService.start_session(
        db=db_session, user_id="user_42", duration_minutes=25
    )
    mock_publisher.publish.reset_mock()

    # Complete it
    completed = await SessionService.complete_session(
        db=db_session, session_id=str(session.id)
    )
    mock_publisher.publish.assert_called_once()
    call_kwargs = mock_publisher.publish.call_args[1]
    assert call_kwargs["event_type"] == "session.completed"
    assert call_kwargs["user_id"] == "user_42"
    assert "session_id" in call_kwargs["payload"]
    assert "actual_duration" in call_kwargs["payload"]


@pytest.mark.asyncio
async def test_pause_session_publishes_event(db_session, mock_publisher):
    session = await SessionService.start_session(
        db=db_session, user_id="user_42", duration_minutes=25
    )
    mock_publisher.publish.reset_mock()

    await SessionService.pause_session(db=db_session, session_id=str(session.id))
    mock_publisher.publish.assert_called_once()
    call_kwargs = mock_publisher.publish.call_args[1]
    assert call_kwargs["event_type"] == "session.paused"


@pytest.mark.asyncio
async def test_resume_session_publishes_event(db_session, mock_publisher):
    session = await SessionService.start_session(
        db=db_session, user_id="user_42", duration_minutes=25
    )
    await SessionService.pause_session(db=db_session, session_id=str(session.id))
    mock_publisher.publish.reset_mock()

    await SessionService.resume_session(db=db_session, session_id=str(session.id))
    mock_publisher.publish.assert_called_once()
    call_kwargs = mock_publisher.publish.call_args[1]
    assert call_kwargs["event_type"] == "session.resumed"


@pytest.mark.asyncio
async def test_no_publish_when_publisher_not_set(db_session):
    SessionService.set_publisher(None)
    session = await SessionService.start_session(
        db=db_session, user_id="user_99", duration_minutes=25
    )
    # Should not raise, even without a publisher
    assert session is not None
