"""Tests for FocusSession ORM model — verify required columns exist."""

import sys
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine, inspect, String, JSON, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# ---------------------------------------------------------------------------
# Bootstrap: patch PostgreSQL-only types and the settings module *before*
# any production code is imported so that module-level side-effects
# (e.g. create_engine with a postgres URL) never fire.
# ---------------------------------------------------------------------------

# 1. Patch postgresql dialect types for SQLite compatibility
import sqlalchemy.dialects.postgresql as _pg

_OrigUUID = _pg.UUID
_OrigARRAY = _pg.ARRAY


class _FakeUUID(String):
    """Drop-in for postgresql.UUID that works on SQLite."""
    def __init__(self, as_uuid=False, **kw):
        super().__init__(length=36)


_pg.UUID = _FakeUUID
_pg.ARRAY = lambda *a, **kw: JSON()

# 2. Provide a fake Base via a mock connection module so that
#    `from database.connection import Base` resolves without touching postgres.
#    We insert a synthetic module into sys.modules.
_test_base_module = MagicMock()


class _TestBase(DeclarativeBase):
    pass


_test_base_module.Base = _TestBase
_test_base_module.get_database = MagicMock()
_test_base_module.get_db = MagicMock()

# Also mock config.settings so it never reads real env
_test_settings_module = MagicMock()
_test_settings_module.get_settings = MagicMock(return_value=MagicMock(
    database_url="sqlite:///:memory:", debug_mode=False
))
sys.modules.setdefault("database", MagicMock())
sys.modules["database.connection"] = _test_base_module
sys.modules.setdefault("config", MagicMock())
sys.modules["config.settings"] = _test_settings_module

# 3. NOW import the model — it will use our fake Base
from models.session_models import FocusSession  # noqa: E402


class TestFocusSessionModel:
    """Verify the FocusSession ORM model has all required columns."""

    @pytest.fixture(autouse=True, scope="class")
    def setup_db(self, request):
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(engine, "connect")
        def _pragma(dbapi_conn, _rec):
            dbapi_conn.cursor().execute("PRAGMA foreign_keys=ON")

        _TestBase.metadata.create_all(bind=engine)

        request.cls._engine = engine
        request.cls._model = FocusSession
        request.cls._inspector = inspect(engine)

    def _columns(self):
        return {c["name"] for c in self._inspector.get_columns(self._model.__tablename__)}

    # --- Assertions ----------------------------------------------------------

    def test_tablename_is_fe_focus_sessions(self):
        assert self._model.__tablename__ == "fe_focus_sessions"

    def test_has_status_column(self):
        assert "status" in self._columns()

    def test_has_paused_at_column(self):
        assert "paused_at" in self._columns()

    def test_has_resumed_at_column(self):
        assert "resumed_at" in self._columns()

    def test_has_planned_end_time_column(self):
        assert "planned_end_time" in self._columns()

    def test_has_completion_reason_column(self):
        assert "completion_reason" in self._columns()
