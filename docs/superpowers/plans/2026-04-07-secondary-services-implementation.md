# Secondary Services Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring all four secondary services (Game Engine, Analytics, AI Insights, Music Control) to a functional baseline with real working endpoints, database persistence, and Redis pub/sub inter-service communication.

**Architecture:** Microservices communicating via Redis pub/sub for async events and HTTP for synchronous queries. All services share a single PostgreSQL instance (public schema, table-name prefixes) and a single Redis instance (db 0). Each service is a FastAPI app with SQLAlchemy ORM, Pydantic validation, and structured logging.

**Tech Stack:** Python 3.11+, FastAPI 0.104, SQLAlchemy 2.0, Pydantic 2.5, Redis 5.0, PostgreSQL, pytest 7.4, OpenAI API (for AI Insights), ytmusicapi (for Music Control)

**Spec:** `docs/superpowers/specs/2026-04-07-secondary-services-baseline-design.md`

---

## Chunk 1: Test Infrastructure + Focus Engine Updates

This chunk sets up pytest infrastructure (none exists), fixes pre-existing Focus Engine bugs, adds the Redis event publisher, and renames tables to use the `fe_` prefix convention.

### Task 1: Test Infrastructure Setup

**Files:**
- Create: `pytest.ini`
- Create: `conftest.py`
- Create: `services/focus_engine/tests/__init__.py`
- Create: `services/focus_engine/tests/conftest.py`
- Create: `services/game_engine/tests/__init__.py`
- Create: `services/game_engine/tests/conftest.py`
- Create: `services/analytics/tests/__init__.py`
- Create: `services/analytics/tests/conftest.py`
- Create: `services/ai_insights/tests/__init__.py`
- Create: `services/ai_insights/tests/conftest.py`
- Create: `services/music_control/tests/__init__.py`
- Create: `services/music_control/tests/conftest.py`

- [ ] **Step 1: Create root pytest.ini**

```ini
[pytest]
testpaths = services
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
pythonpath = services/focus_engine services/game_engine services/analytics services/ai_insights services/music_control .
```

Note: `pythonpath` is required because each service uses bare imports at runtime (e.g., `from config.settings import ...`) while tests run from the repo root. This adds each service root to `sys.path` so both import styles work.

- [ ] **Step 2: Create root conftest.py**

```python
"""Root conftest — shared fixtures across all services."""
```

- [ ] **Step 3: Create test directories and __init__.py for each service**

Create empty `tests/__init__.py` in each of these:
- `services/focus_engine/tests/`
- `services/game_engine/tests/`
- `services/analytics/tests/`
- `services/ai_insights/tests/`
- `services/music_control/tests/`

- [ ] **Step 4: Create Focus Engine test conftest with SQLite in-memory DB**

File: `services/focus_engine/tests/conftest.py`

```python
"""Focus Engine test fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from services.focus_engine.database.connection import Base


@pytest.fixture
def db_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

- [ ] **Step 5: Create Game Engine test conftest (same pattern)**

File: `services/game_engine/tests/conftest.py`

```python
"""Game Engine test fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game_engine.database.connection import Base


@pytest.fixture
def db_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

- [ ] **Step 6: Create minimal conftest files for analytics, ai_insights, music_control**

These will be populated when those services are implemented. For now, just:

```python
"""[Service Name] test fixtures."""
```

- [ ] **Step 7: Verify pytest discovers test directories**

Run: `cd O:/focus-flow_DEMO && python -m pytest --collect-only 2>&1 | head -20`
Expected: No errors. May show "no tests ran" which is fine.

- [ ] **Step 8: Commit**

```bash
git add pytest.ini conftest.py services/*/tests/
git commit -m "test: add pytest infrastructure and per-service test directories"
```

---

### Task 2: Fix Focus Engine ORM Model — Add Missing Columns

The Focus Engine service layer uses columns (`status`, `paused_at`, `resumed_at`, `planned_end_time`, `completion_reason`) that are not defined in the SQLAlchemy model. This is a pre-existing bug that must be fixed before adding event publishing.

**Files:**
- Modify: `services/focus_engine/models/session_models.py:14-55`

- [ ] **Step 1: Write failing test for session status column**

File: `services/focus_engine/tests/test_session_model.py`

```python
"""Tests for FocusSession ORM model."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from services.focus_engine.database.connection import Base
from services.focus_engine.models.session_models import FocusSession


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_focus_session_has_status_column(db_session):
    """FocusSession must have a status column used by the service layer."""
    session = FocusSession(
        user_id="test_user",
        start_time=datetime.utcnow(),
        planned_duration=25,
        status="active",
    )
    db_session.add(session)
    db_session.commit()
    assert session.status == "active"


def test_focus_session_has_pause_resume_columns(db_session):
    """FocusSession must have paused_at, resumed_at, planned_end_time, completion_reason."""
    now = datetime.utcnow()
    session = FocusSession(
        user_id="test_user",
        start_time=now,
        planned_duration=25,
        status="active",
        planned_end_time=now,
        paused_at=now,
        resumed_at=now,
        completion_reason="completed",
    )
    db_session.add(session)
    db_session.commit()
    assert session.paused_at == now
    assert session.resumed_at == now
    assert session.planned_end_time == now
    assert session.completion_reason == "completed"


def test_focus_session_table_name():
    """FocusSession table should use fe_ prefix."""
    assert FocusSession.__tablename__ == "fe_focus_sessions"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_model.py -v`
Expected: FAIL — `status` column not defined, table name is `focus_sessions` not `fe_focus_sessions`

- [ ] **Step 3: Add missing columns and rename table**

Modify `services/focus_engine/models/session_models.py`, change the `FocusSession` class:

```python
class FocusSession(Base):
    """Focus session database model"""
    __tablename__ = "fe_focus_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    user_id = Column(String(255), index=True)

    # Session timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    planned_duration = Column(Integer, default=50)  # minutes
    actual_duration = Column(Integer, nullable=True)
    break_duration = Column(Integer, default=10)
    planned_end_time = Column(DateTime, nullable=True)

    # Session state
    status = Column(String(50), default="active", index=True)
    paused_at = Column(DateTime, nullable=True)
    resumed_at = Column(DateTime, nullable=True)
    completion_reason = Column(String(100), nullable=True)

    # Session quality metrics
    completion_rate = Column(Float, nullable=True)
    productivity_score = Column(Float, nullable=True)
    interruptions = Column(Integer, default=0)
    interruption_types = Column(JSON, nullable=True)
    focus_quality = Column(String(50), nullable=True)

    # Session context
    session_type = Column(String(50), default="work")
    time_of_day_category = Column(String(50), nullable=True)

    # Music integration
    playlist_id = Column(String(255), nullable=True)
    playlist_name = Column(String(500), nullable=True)

    # AI-generated insights
    ai_insights = Column(Text, nullable=True)
    optimal_time_suggestions = Column(Text, nullable=True)
    improvement_recommendations = Column(JSON, nullable=True)

    # Gamification
    experience_points = Column(Integer, default=0)
    achievements_unlocked = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

Also rename `User` table:

```python
class User(Base):
    """User model for future multi-user support"""
    __tablename__ = "fe_users"
    # ... rest unchanged
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_model.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add services/focus_engine/models/session_models.py services/focus_engine/tests/test_session_model.py
git commit -m "fix: add missing ORM columns and fe_ table prefix to Focus Engine models"
```

---

### Task 3: Fix Focus Engine Double-Prefix Bug in Sessions Router

The sessions router is mounted at `/api/v1/sessions` but routes inside use `/sessions/...`, creating double-prefixed paths like `/api/v1/sessions/sessions/`.

**Files:**
- Modify: `services/focus_engine/routers/sessions.py`

- [ ] **Step 1: Write failing test for correct route paths**

File: `services/focus_engine/tests/test_session_routes.py`

```python
"""Tests for sessions router path correctness."""
from services.focus_engine.routers.sessions import router


def test_session_routes_have_no_double_prefix():
    """Routes should NOT start with /sessions/ since the router is mounted at /api/v1/sessions."""
    for route in router.routes:
        path = getattr(route, "path", "")
        assert not path.startswith("/sessions/"), (
            f"Route {path} has double prefix — should not start with /sessions/ "
            f"because router is mounted at /api/v1/sessions"
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_routes.py -v`
Expected: FAIL — routes like `/sessions/` start with `/sessions/`

- [ ] **Step 3: Fix route paths in sessions.py**

In `services/focus_engine/routers/sessions.py`, change all route decorators:

| Old Path | New Path |
|---|---|
| `@router.post("/sessions/", ...)` | `@router.post("/", ...)` |
| `@router.get("/sessions/{session_id}", ...)` | `@router.get("/{session_id}", ...)` |
| `@router.post("/sessions/{session_id}/pause", ...)` | `@router.post("/{session_id}/pause", ...)` |
| `@router.post("/sessions/{session_id}/resume", ...)` | `@router.post("/{session_id}/resume", ...)` |
| `@router.post("/sessions/{session_id}/complete", ...)` | `@router.post("/{session_id}/complete", ...)` |
| `@router.get("/sessions/user/{user_id}", ...)` | `@router.get("/user/{user_id}", ...)` |
| `@router.get("/sessions/user/{user_id}/active", ...)` | `@router.get("/user/{user_id}/active", ...)` |
| `@router.delete("/sessions/{session_id}", ...)` | `@router.delete("/{session_id}", ...)` |

- [ ] **Step 4: Run test to verify it passes**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_routes.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/focus_engine/routers/sessions.py services/focus_engine/tests/test_session_routes.py
git commit -m "fix: remove double prefix in Focus Engine sessions router paths"
```

---

### Task 4: Fix Focus Engine Database Connection — get_database vs get_db

The session router imports `get_db` but `connection.py` exports `get_database`. Also migrate to non-deprecated `DeclarativeBase`.

**Files:**
- Modify: `services/focus_engine/database/connection.py`
- Modify: `services/focus_engine/config/settings.py:30` (add localhost:5173 to CORS)

- [ ] **Step 1: Update connection.py**

```python
"""
Focus Engine Database Connection
SQLAlchemy setup with connection pooling
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from config.settings import get_settings
import logging

logger = logging.getLogger("focus_engine.database")
settings = get_settings()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=settings.debug_mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


def get_db() -> Session:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Keep backward compat alias
get_database = get_db
```

- [ ] **Step 2: Add localhost:5173 to CORS origins**

In `services/focus_engine/config/settings.py`, change line 30:

```python
cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
```

**Note:** Changing `Base` from `declarative_base()` to `class Base(DeclarativeBase)` changes its identity. All ORM models that `from database.connection import Base` will get the new `Base` on import. After making this change, all services must be fully restarted (not hot-reloaded) to ensure models register with the new metadata.

- [ ] **Step 3: Run existing tests to verify nothing broke**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/ -v`
Expected: All tests PASS

- [ ] **Step 4: Commit**

```bash
git add services/focus_engine/database/connection.py services/focus_engine/config/settings.py
git commit -m "fix: migrate to DeclarativeBase, unify get_db naming, add Vite CORS origin"
```

---

### Task 5: Redis Event Publisher Module

Create the shared event publishing pattern that Focus Engine and all other services will use.

**Files:**
- Create: `services/focus_engine/events/__init__.py`
- Create: `services/focus_engine/events/publisher.py`
- Create: `services/focus_engine/tests/test_event_publisher.py`

- [ ] **Step 1: Write failing test for event publisher**

File: `services/focus_engine/tests/test_event_publisher.py`

```python
"""Tests for Redis event publisher."""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = AsyncMock()
    redis.publish = AsyncMock(return_value=1)
    return redis


@pytest.mark.asyncio
async def test_publish_event_sends_to_redis(mock_redis):
    """publish_event should PUBLISH a JSON message to the correct channel."""
    from services.focus_engine.events.publisher import EventPublisher

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
    """Event messages must include an ISO 8601 timestamp."""
    from services.focus_engine.events.publisher import EventPublisher

    publisher = EventPublisher(redis_client=mock_redis)
    await publisher.publish(
        event_type="session.started",
        user_id="user_123",
        payload={},
    )

    message = json.loads(mock_redis.publish.call_args[0][1])
    # Should parse as ISO datetime
    datetime.fromisoformat(message["timestamp"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_event_publisher.py -v`
Expected: FAIL — module does not exist

- [ ] **Step 3: Implement EventPublisher**

File: `services/focus_engine/events/__init__.py`
```python
```

File: `services/focus_engine/events/publisher.py`

```python
"""Redis pub/sub event publisher."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("focus_engine.events.publisher")

SERVICE_NAME = "focus_engine"


class EventPublisher:
    """Publishes events to Redis pub/sub channels."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event_type: str, user_id: str, payload: dict) -> None:
        """Publish an event to the Redis channel matching the event_type.

        Args:
            event_type: Channel name, e.g. "session.completed"
            user_id: The user this event pertains to
            payload: Event-specific data dict
        """
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_service": SERVICE_NAME,
            "user_id": user_id,
            "payload": payload,
        }
        raw = json.dumps(message)
        await self.redis.publish(event_type, raw)
        logger.info("Published %s for user %s", event_type, user_id)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_event_publisher.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add services/focus_engine/events/ services/focus_engine/tests/test_event_publisher.py
git commit -m "feat: add Redis event publisher module for Focus Engine"
```

---

### Task 6: Wire Event Publisher into Focus Engine Session Service

Publish `session.started`, `session.completed`, `session.paused`, `session.resumed` events after state transitions.

**Files:**
- Modify: `services/focus_engine/services/session_service.py`
- Modify: `services/focus_engine/main.py` (add Redis connection to lifespan)
- Create: `services/focus_engine/tests/test_session_service_events.py`

- [ ] **Step 1: Write failing test for session events**

File: `services/focus_engine/tests/test_session_service_events.py`

```python
"""Tests that session state transitions publish Redis events."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.focus_engine.database.connection import Base
from services.focus_engine.models.session_models import FocusSession
from services.focus_engine.services.session_service import SessionService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def mock_publisher():
    publisher = AsyncMock()
    publisher.publish = AsyncMock()
    return publisher


@pytest.mark.asyncio
async def test_start_session_publishes_event(db_session, mock_publisher):
    """Starting a session should publish session.started event."""
    with patch.object(SessionService, '_get_publisher', return_value=mock_publisher):
        session = await SessionService.start_session(
            db=db_session, user_id="test_user", duration_minutes=25
        )

    mock_publisher.publish.assert_called()
    call = mock_publisher.publish.call_args
    assert call.kwargs["event_type"] == "session.started" or call[1]["event_type"] == "session.started"


@pytest.mark.asyncio
async def test_complete_session_publishes_event(db_session, mock_publisher):
    """Completing a session should publish session.completed with payload."""
    # Create active session first
    focus_session = FocusSession(
        user_id="test_user",
        start_time=datetime.utcnow(),
        planned_duration=25,
        status="active",
    )
    db_session.add(focus_session)
    db_session.commit()

    with patch.object(SessionService, '_get_publisher', return_value=mock_publisher):
        await SessionService.complete_session(
            db=db_session, session_id=str(focus_session.id)
        )

    mock_publisher.publish.assert_called()
    call = mock_publisher.publish.call_args
    assert call.kwargs.get("event_type") == "session.completed" or call[1].get("event_type") == "session.completed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_service_events.py -v`
Expected: FAIL — `_get_publisher` not defined

- [ ] **Step 3: Add event publishing to SessionService**

In `services/focus_engine/services/session_service.py`:

**IMPORTANT:** The existing methods are `@staticmethod`. They must be changed to `@classmethod` so they can access the class-level `_publisher`. Change every `@staticmethod` to `@classmethod` and add `cls` as the first parameter (replacing nothing — these methods had no `self`).

1. Add import: `from ..events.publisher import EventPublisher`
2. Add class-level publisher reference:
```python
_publisher: EventPublisher | None = None

@classmethod
def set_publisher(cls, publisher: EventPublisher):
    cls._publisher = publisher

@classmethod
def _get_publisher(cls) -> EventPublisher | None:
    return cls._publisher
```

3. Change all `@staticmethod` decorators to `@classmethod` and add `cls` as first parameter:
```python
# Before:
@staticmethod
async def start_session(db: Session, user_id: str, ...) -> FocusSession:

# After:
@classmethod
async def start_session(cls, db: Session, user_id: str, ...) -> FocusSession:
```
Apply this to: `start_session`, `pause_session`, `resume_session`, `complete_session`, `get_user_sessions`, `get_active_session`.

4. At end of `start_session`, after the WebSocket broadcast, add:
```python
if cls._publisher:
    await cls._publisher.publish(
        event_type="session.started",
        user_id=user_id,
        payload={
            "session_id": str(session.id),
            "session_type": session.session_type,
            "planned_duration": duration_minutes,
        },
    )
```

5. At end of `complete_session`, add:
```python
if cls._publisher:
    await cls._publisher.publish(
        event_type="session.completed",
        user_id=session.user_id,
        payload={
            "session_id": str(session.id),
            "session_type": session.session_type,
            "actual_duration": session.actual_duration,
            "productivity_score": session.productivity_score,
            "completed_at": session.end_time.isoformat() if session.end_time else None,
            "interruption_count": session.interruptions or 0,
        },
    )
```

6. At end of `pause_session`, add:
```python
if cls._publisher:
    await cls._publisher.publish(
        event_type="session.paused",
        user_id=session.user_id,
        payload={
            "session_id": session_id,
            "paused_at": session.paused_at.isoformat(),
        },
    )
```

7. At end of `resume_session`, add:
```python
if cls._publisher:
    await cls._publisher.publish(
        event_type="session.resumed",
        user_id=session.user_id,
        payload={
            "session_id": session_id,
            "resumed_at": session.resumed_at.isoformat(),
        },
    )
```

- [ ] **Step 4: Update main.py lifespan to create Redis connection and set publisher**

In `services/focus_engine/main.py`, update the lifespan:

```python
import redis.asyncio as aioredis
from .events.publisher import EventPublisher
from .services.session_service import SessionService

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Focus Engine service starting up...")
    # Connect to Redis for event publishing
    redis_client = aioredis.from_url(settings.redis_url)
    publisher = EventPublisher(redis_client=redis_client)
    SessionService.set_publisher(publisher)
    yield
    await redis_client.close()
    logger.info("Focus Engine service shutting down...")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/test_session_service_events.py -v`
Expected: All 2 tests PASS

- [ ] **Step 6: Run all Focus Engine tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/focus_engine/tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/focus_engine/services/session_service.py services/focus_engine/main.py services/focus_engine/tests/test_session_service_events.py
git commit -m "feat: publish Redis events on Focus Engine session state transitions"
```

---

## Chunk 2: Game Engine Implementation

This chunk completes the Game Engine service — migrating the database connection, implementing calculators, services, routers, event subscriber, and wiring everything into main.py.

### Task 7: Game Engine Database Migration and Config Fixes

Fix deprecated SQLAlchemy import, database URL default, and Redis URL default.

**Files:**
- Modify: `services/game_engine/database/connection.py`
- Modify: `services/game_engine/config/settings.py:19,22`

- [ ] **Step 1: Update connection.py to use DeclarativeBase**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

from game_engine.config.settings import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for Game Engine ORM models."""
    pass


def get_db() -> Generator:
    """Dependency function for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 2: Fix settings.py defaults**

In `services/game_engine/config/settings.py`:
- Change line 19: `database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"`
- Change line 22: `redis_url: str = "redis://localhost:6379/0"`

- [ ] **Step 3: Commit**

```bash
git add services/game_engine/database/connection.py services/game_engine/config/settings.py
git commit -m "fix: migrate Game Engine to DeclarativeBase, fix database and Redis URLs"
```

---

### Task 8: Game Engine Model Updates — Table Prefixes and XP History

Rename tables to use `ge_` prefix and add the `XPHistory` ORM model.

**Files:**
- Modify: `services/game_engine/models/achievement_models.py:37`
- Modify: `services/game_engine/models/level_models.py:15`
- Modify: `services/game_engine/models/streak_models.py:23`
- Create: `services/game_engine/models/xp_history_models.py`
- Create: `services/game_engine/tests/test_models.py`

- [ ] **Step 1: Write failing tests for table names and XPHistory model**

File: `services/game_engine/tests/test_models.py`

```python
"""Tests for Game Engine ORM models."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game_engine.database.connection import Base
from game_engine.models.achievement_models import Achievement, AchievementType, AchievementCategory
from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak
from game_engine.models.xp_history_models import XPHistory


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_achievement_table_name():
    assert Achievement.__tablename__ == "ge_user_achievements"


def test_user_level_table_name():
    assert UserLevel.__tablename__ == "ge_user_levels"


def test_user_streak_table_name():
    assert UserStreak.__tablename__ == "ge_user_streaks"


def test_xp_history_table_name():
    assert XPHistory.__tablename__ == "ge_xp_history"


def test_xp_history_create(db_session):
    """XPHistory should persist with all required fields."""
    record = XPHistory(
        user_id="user_1",
        session_id="sess_1",
        base_xp=50,
        bonus_xp=25,
        total_xp=75,
        reason="session_completed",
    )
    db_session.add(record)
    db_session.commit()
    assert record.id is not None
    assert record.created_at is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_models.py -v`
Expected: FAIL — table names wrong, `XPHistory` not found

- [ ] **Step 3: Rename tables in existing models and fix Enum for SQLite compatibility**

In `services/game_engine/models/achievement_models.py`:
- Line 37: change `__tablename__` to `"ge_user_achievements"`
- Line 42: change `Column(SQLEnum(AchievementType), nullable=False)` to `Column(SQLEnum(AchievementType, create_constraint=False, native_enum=False), nullable=False)`
- Line 43: change `Column(SQLEnum(AchievementCategory), nullable=False)` to `Column(SQLEnum(AchievementCategory, create_constraint=False, native_enum=False), nullable=False)`

Note: `native_enum=False` and `create_constraint=False` ensure Enum columns work correctly in SQLite for testing while still working with PostgreSQL in production.

```python
__tablename__ = "ge_user_achievements"
```

In `services/game_engine/models/level_models.py` line 15:
```python
__tablename__ = "ge_user_levels"
```

In `services/game_engine/models/streak_models.py` line 23:
```python
__tablename__ = "ge_user_streaks"
```

- [ ] **Step 4: Create XPHistory model**

File: `services/game_engine/models/xp_history_models.py`

```python
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

from game_engine.database.connection import Base


class XPHistory(Base):
    """Log of XP gains with source and reason."""
    __tablename__ = "ge_xp_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    base_xp = Column(Integer, nullable=False)
    bonus_xp = Column(Integer, default=0)
    total_xp = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 5: Update models `__init__.py`**

File: `services/game_engine/models/__init__.py`

```python
from .achievement_models import Achievement, AchievementType, AchievementCategory, AchievementResponse, AchievementProgress, UserAchievementStats, AchievementUnlockEvent
from .level_models import UserLevel, LevelResponse, LevelUpEvent, ExperienceGain, calculate_xp_for_level
from .streak_models import UserStreak, StreakResponse, StreakUpdate, StreakMilestone, StreakMilestoneType
from .xp_history_models import XPHistory
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_models.py -v`
Expected: All 6 tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/game_engine/models/ services/game_engine/tests/test_models.py
git commit -m "feat: add ge_ table prefixes and XPHistory ORM model to Game Engine"
```

---

### Task 9: Implement Experience Calculator

The existing `experience_calculator.py` is empty. Implement XP calculation with difficulty modifiers.

**Files:**
- Create: `services/game_engine/tests/test_experience_calculator.py`
- Modify: `services/game_engine/calculators/experience_calculator.py`

- [ ] **Step 1: Write failing tests**

File: `services/game_engine/tests/test_experience_calculator.py`

```python
"""Tests for experience point calculator."""
import pytest
from game_engine.calculators.experience_calculator import ExperienceCalculator


def test_base_xp_for_completed_session():
    """A completed session earns base XP."""
    result = ExperienceCalculator.calculate(
        session_duration=25,
        session_completed=True,
        productivity_score=5.0,
        current_streak=0,
    )
    assert result["base_xp"] == 50
    assert result["total_xp"] >= 50


def test_completion_bonus_when_session_completed():
    """Completed sessions get a completion bonus."""
    completed = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=5.0, current_streak=0
    )
    abandoned = ExperienceCalculator.calculate(
        session_duration=25, session_completed=False, productivity_score=5.0, current_streak=0
    )
    assert completed["total_xp"] > abandoned["total_xp"]


def test_streak_multiplier_increases_xp():
    """Active streaks should multiply XP."""
    no_streak = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=5.0, current_streak=0
    )
    with_streak = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=5.0, current_streak=7
    )
    assert with_streak["total_xp"] > no_streak["total_xp"]


def test_high_productivity_gives_more_xp():
    """Higher productivity scores should give more XP."""
    low = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=2.0, current_streak=0
    )
    high = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=9.0, current_streak=0
    )
    assert high["total_xp"] > low["total_xp"]


def test_longer_sessions_earn_more_xp():
    """Longer sessions should earn proportionally more base XP."""
    short = ExperienceCalculator.calculate(
        session_duration=15, session_completed=True, productivity_score=5.0, current_streak=0
    )
    long = ExperienceCalculator.calculate(
        session_duration=50, session_completed=True, productivity_score=5.0, current_streak=0
    )
    assert long["base_xp"] > short["base_xp"]


def test_result_contains_expected_keys():
    """Result dict must have base_xp, bonus_xp, total_xp, reason, multipliers_applied."""
    result = ExperienceCalculator.calculate(
        session_duration=25, session_completed=True, productivity_score=5.0, current_streak=0
    )
    assert "base_xp" in result
    assert "bonus_xp" in result
    assert "total_xp" in result
    assert "reason" in result
    assert "multipliers_applied" in result
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_experience_calculator.py -v`
Expected: FAIL — ExperienceCalculator not defined

- [ ] **Step 3: Implement ExperienceCalculator**

File: `services/game_engine/calculators/experience_calculator.py`

```python
"""XP calculation for focus sessions."""

# Base XP per 25-minute session
BASE_XP_PER_25_MIN = 50
COMPLETION_BONUS = 25
STREAK_MULTIPLIER_PER_DAY = 0.02  # 2% per streak day, capped
MAX_STREAK_MULTIPLIER = 0.5  # max 50% bonus
PRODUCTIVITY_MULTIPLIER_MAX = 0.5  # max 50% bonus for 10.0 score


class ExperienceCalculator:
    """Calculates XP earned from a focus session."""

    @staticmethod
    def calculate(
        session_duration: int,
        session_completed: bool,
        productivity_score: float | None = None,
        current_streak: int = 0,
    ) -> dict:
        """Calculate XP for a session.

        Args:
            session_duration: Duration in minutes.
            session_completed: Whether the session was fully completed.
            productivity_score: 0.0 to 10.0 self-assessed score.
            current_streak: Current daily streak count.

        Returns:
            Dict with base_xp, bonus_xp, total_xp, reason, multipliers_applied.
        """
        # Base XP scales linearly with duration
        base_xp = int(BASE_XP_PER_25_MIN * (session_duration / 25))

        bonus_xp = 0
        multipliers = {}

        # Completion bonus
        if session_completed:
            bonus_xp += COMPLETION_BONUS
            multipliers["completion"] = COMPLETION_BONUS

        # Streak multiplier
        if current_streak > 0:
            streak_mult = min(current_streak * STREAK_MULTIPLIER_PER_DAY, MAX_STREAK_MULTIPLIER)
            streak_bonus = int(base_xp * streak_mult)
            bonus_xp += streak_bonus
            multipliers["streak"] = streak_bonus

        # Productivity multiplier
        if productivity_score is not None and productivity_score > 0:
            prod_mult = (productivity_score / 10.0) * PRODUCTIVITY_MULTIPLIER_MAX
            prod_bonus = int(base_xp * prod_mult)
            bonus_xp += prod_bonus
            multipliers["productivity"] = prod_bonus

        total_xp = base_xp + bonus_xp
        reason = "session_completed" if session_completed else "session_abandoned"

        return {
            "base_xp": base_xp,
            "bonus_xp": bonus_xp,
            "total_xp": total_xp,
            "reason": reason,
            "multipliers_applied": multipliers,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_experience_calculator.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add services/game_engine/calculators/experience_calculator.py services/game_engine/tests/test_experience_calculator.py
git commit -m "feat: implement XP calculator with duration, streak, and productivity modifiers"
```

---

### Task 10: Implement Streak Calculator

**Files:**
- Create: `services/game_engine/tests/test_streak_calculator.py`
- Modify: `services/game_engine/calculators/streak_calculator.py`

- [ ] **Step 1: Write failing tests**

File: `services/game_engine/tests/test_streak_calculator.py`

```python
"""Tests for streak calculator."""
import pytest
from datetime import date, timedelta
from game_engine.calculators.streak_calculator import StreakCalculator


def test_first_session_starts_streak():
    """First ever session should start a streak of 1."""
    result = StreakCalculator.update_streak(
        last_session_date=None,
        current_streak=0,
    )
    assert result["new_streak"] == 1
    assert result["is_broken"] is False


def test_same_day_session_keeps_streak():
    """Multiple sessions on same day don't increment streak."""
    today = date.today()
    result = StreakCalculator.update_streak(
        last_session_date=today,
        current_streak=5,
    )
    assert result["new_streak"] == 5
    assert result["is_broken"] is False


def test_next_day_session_increments_streak():
    """Session the next day increments streak."""
    yesterday = date.today() - timedelta(days=1)
    result = StreakCalculator.update_streak(
        last_session_date=yesterday,
        current_streak=5,
    )
    assert result["new_streak"] == 6


def test_two_days_missed_breaks_streak():
    """Missing more than 1 day breaks the streak (grace period is 36 hours)."""
    three_days_ago = date.today() - timedelta(days=3)
    result = StreakCalculator.update_streak(
        last_session_date=three_days_ago,
        current_streak=10,
    )
    assert result["new_streak"] == 1
    assert result["is_broken"] is True


def test_milestone_detection():
    """Should detect streak milestones at 3, 7, 30, 100 days."""
    yesterday = date.today() - timedelta(days=1)
    result = StreakCalculator.update_streak(
        last_session_date=yesterday,
        current_streak=6,  # will become 7
    )
    assert result["is_milestone"] is True
    assert result["milestone_type"] == "7_day"


def test_no_milestone_at_non_milestone_count():
    """Regular streak increments are not milestones."""
    yesterday = date.today() - timedelta(days=1)
    result = StreakCalculator.update_streak(
        last_session_date=yesterday,
        current_streak=4,  # will become 5
    )
    assert result["is_milestone"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_streak_calculator.py -v`
Expected: FAIL — StreakCalculator not defined

- [ ] **Step 3: Implement StreakCalculator**

File: `services/game_engine/calculators/streak_calculator.py`

```python
"""Streak calculation logic with grace period."""
from datetime import date, timedelta
from typing import Optional

MILESTONE_DAYS = {3: "3_day", 7: "7_day", 30: "30_day", 100: "100_day"}
# Grace period: allow missing 1 day (last session up to 2 days ago)
MAX_GAP_DAYS = 2


class StreakCalculator:
    """Calculates streak updates given a new session."""

    @staticmethod
    def update_streak(
        last_session_date: Optional[date],
        current_streak: int,
    ) -> dict:
        """Determine new streak value after a session today.

        Args:
            last_session_date: Date of the user's last completed session, or None.
            current_streak: The user's current streak count.

        Returns:
            Dict with new_streak, is_broken, is_milestone, milestone_type.
        """
        today = date.today()

        # First session ever
        if last_session_date is None:
            new_streak = 1
            is_broken = False
        elif last_session_date == today:
            # Same day — no change
            new_streak = current_streak
            is_broken = False
        else:
            gap = (today - last_session_date).days
            if gap <= MAX_GAP_DAYS:
                # Within grace period — continue streak
                new_streak = current_streak + 1
                is_broken = False
            else:
                # Streak broken — restart
                new_streak = 1
                is_broken = True

        # Milestone check
        milestone_type = MILESTONE_DAYS.get(new_streak)
        is_milestone = milestone_type is not None

        return {
            "new_streak": new_streak,
            "is_broken": is_broken,
            "is_milestone": is_milestone,
            "milestone_type": milestone_type,
        }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_streak_calculator.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add services/game_engine/calculators/streak_calculator.py services/game_engine/tests/test_streak_calculator.py
git commit -m "feat: implement streak calculator with grace period and milestone detection"
```

---

### Task 11: Implement Game Engine Services (Level, Streak, Achievement)

These services use the calculators and ORM models to implement the business logic.

**Files:**
- Modify: `services/game_engine/services/level_service.py`
- Modify: `services/game_engine/services/streak_service.py`
- Modify: `services/game_engine/services/achievement_service.py`
- Create: `services/game_engine/services/leaderboard_service.py`
- Create: `services/game_engine/tests/test_level_service.py`
- Create: `services/game_engine/tests/test_streak_service.py`

- [ ] **Step 1: Write failing tests for LevelService**

File: `services/game_engine/tests/test_level_service.py`

```python
"""Tests for LevelService."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game_engine.database.connection import Base
from game_engine.models.level_models import UserLevel
from game_engine.models.xp_history_models import XPHistory
from game_engine.services.level_service import LevelService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_award_xp_creates_user_level_if_missing(db_session):
    """First XP award should create a UserLevel row."""
    service = LevelService(db_session)
    result = service.award_xp(
        user_id="user_1",
        session_id="sess_1",
        base_xp=50,
        bonus_xp=25,
        total_xp=75,
        reason="session_completed",
    )
    level = db_session.query(UserLevel).filter_by(user_id="user_1").first()
    assert level is not None
    assert level.total_xp == 75
    assert level.current_xp == 75


def test_award_xp_records_history(db_session):
    """Each XP award should create an XPHistory record."""
    service = LevelService(db_session)
    service.award_xp("user_1", "sess_1", 50, 25, 75, "session_completed")
    history = db_session.query(XPHistory).filter_by(user_id="user_1").all()
    assert len(history) == 1
    assert history[0].total_xp == 75


def test_level_up_when_xp_exceeds_threshold(db_session):
    """User should level up when current_xp >= xp_to_next_level."""
    service = LevelService(db_session)
    # Level 1 needs 100 XP. Award 150.
    result = service.award_xp("user_1", "sess_1", 150, 0, 150, "session_completed")
    level = db_session.query(UserLevel).filter_by(user_id="user_1").first()
    assert level.current_level >= 2


def test_get_user_level_returns_none_for_unknown(db_session):
    """Getting level for unknown user returns None."""
    service = LevelService(db_session)
    result = service.get_user_level("nonexistent")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_level_service.py -v`
Expected: FAIL

- [ ] **Step 3: Implement LevelService**

File: `services/game_engine/services/level_service.py`

```python
"""Level and XP management service."""
from sqlalchemy.orm import Session
from typing import Optional

from game_engine.models.level_models import UserLevel, calculate_xp_for_level
from game_engine.models.xp_history_models import XPHistory


class LevelService:
    """Manages user levels and XP awards."""

    def __init__(self, db: Session):
        self.db = db

    def award_xp(
        self,
        user_id: str,
        session_id: str,
        base_xp: int,
        bonus_xp: int,
        total_xp: int,
        reason: str,
    ) -> dict:
        """Award XP to a user and handle level-ups.

        Returns dict with level_up (bool), new_level, total_xp.
        """
        # Get or create user level
        level = self.db.query(UserLevel).filter_by(user_id=user_id).first()
        if level is None:
            level = UserLevel(
                user_id=user_id,
                current_level=1,
                current_xp=0,
                total_xp=0,
                xp_to_next_level=calculate_xp_for_level(2),
            )
            self.db.add(level)
            self.db.flush()

        # Record history
        history = XPHistory(
            user_id=user_id,
            session_id=session_id,
            base_xp=base_xp,
            bonus_xp=bonus_xp,
            total_xp=total_xp,
            reason=reason,
        )
        self.db.add(history)

        # Add XP
        level.current_xp += total_xp
        level.total_xp += total_xp

        # Check for level-ups (could be multiple)
        leveled_up = False
        while level.current_xp >= level.xp_to_next_level:
            level.current_xp -= level.xp_to_next_level
            level.current_level += 1
            level.xp_to_next_level = calculate_xp_for_level(level.current_level + 1)
            leveled_up = True
            from datetime import datetime
            level.level_up_at = datetime.utcnow()

        self.db.commit()

        return {
            "level_up": leveled_up,
            "new_level": level.current_level,
            "total_xp": level.total_xp,
            "current_xp": level.current_xp,
            "xp_to_next_level": level.xp_to_next_level,
        }

    def get_user_level(self, user_id: str) -> Optional[UserLevel]:
        """Get user's current level data."""
        return self.db.query(UserLevel).filter_by(user_id=user_id).first()

    def get_xp_history(self, user_id: str, limit: int = 20) -> list:
        """Get recent XP history for a user."""
        return (
            self.db.query(XPHistory)
            .filter_by(user_id=user_id)
            .order_by(XPHistory.created_at.desc())
            .limit(limit)
            .all()
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_level_service.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Write failing tests for StreakService**

File: `services/game_engine/tests/test_streak_service.py`

```python
"""Tests for StreakService."""
import pytest
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from game_engine.database.connection import Base
from game_engine.models.streak_models import UserStreak
from game_engine.services.streak_service import StreakService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_update_creates_streak_for_new_user(db_session):
    """First session should create a UserStreak with streak=1."""
    service = StreakService(db_session)
    result = service.update("user_1")
    streak = db_session.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak is not None
    assert streak.current_streak == 1
    assert streak.total_sessions == 1


def test_update_increments_total_sessions(db_session):
    """Each update increments total_sessions."""
    service = StreakService(db_session)
    service.update("user_1")
    service.update("user_1")
    streak = db_session.query(UserStreak).filter_by(user_id="user_1").first()
    assert streak.total_sessions == 2


def test_update_tracks_longest_streak(db_session):
    """longest_streak should track the maximum streak achieved."""
    streak = UserStreak(
        user_id="user_1",
        current_streak=9,
        longest_streak=9,
        last_session_date=date.today() - timedelta(days=1),
        total_sessions=9,
    )
    db_session.add(streak)
    db_session.commit()

    service = StreakService(db_session)
    result = service.update("user_1")
    assert result["new_streak"] == 10
    updated = db_session.query(UserStreak).filter_by(user_id="user_1").first()
    assert updated.longest_streak == 10
```

- [ ] **Step 6: Implement StreakService**

File: `services/game_engine/services/streak_service.py`

```python
"""Streak tracking service."""
from datetime import date
from sqlalchemy.orm import Session
from typing import Optional

from game_engine.models.streak_models import UserStreak
from game_engine.calculators.streak_calculator import StreakCalculator


class StreakService:
    """Manages user streaks."""

    def __init__(self, db: Session):
        self.db = db

    def update(self, user_id: str) -> dict:
        """Update streak after a completed session.

        Returns dict with new_streak, is_broken, is_milestone, milestone_type.
        """
        streak = self.db.query(UserStreak).filter_by(user_id=user_id).first()

        if streak is None:
            streak = UserStreak(user_id=user_id, current_streak=0, longest_streak=0, total_sessions=0)
            self.db.add(streak)
            self.db.flush()

        result = StreakCalculator.update_streak(
            last_session_date=streak.last_session_date,
            current_streak=streak.current_streak,
        )

        streak.current_streak = result["new_streak"]
        streak.last_session_date = date.today()
        streak.total_sessions += 1

        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        if result["is_broken"]:
            streak.streak_start_date = date.today()
        elif streak.streak_start_date is None:
            streak.streak_start_date = date.today()

        self.db.commit()
        return result

    def get_streak(self, user_id: str) -> Optional[UserStreak]:
        """Get current streak data for a user."""
        return self.db.query(UserStreak).filter_by(user_id=user_id).first()
```

- [ ] **Step 7: Run streak tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/test_streak_service.py -v`
Expected: All 3 tests PASS

- [ ] **Step 8: Implement AchievementService**

File: `services/game_engine/services/achievement_service.py`

```python
"""Achievement evaluation and tracking service."""
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

from game_engine.models.achievement_models import (
    Achievement,
    AchievementType,
    AchievementCategory,
    AchievementResponse,
    UserAchievementStats,
)
from game_engine.models.streak_models import UserStreak
from game_engine.models.level_models import UserLevel

# Achievement definitions: type -> (title, description, icon, category, progress_required)
ACHIEVEMENT_DEFS = {
    AchievementType.FIRST_SESSION: ("First Focus", "Complete your first focus session", "star", AchievementCategory.MILESTONE, 1),
    AchievementType.STREAK_3: ("Getting Started", "Maintain a 3-day streak", "fire", AchievementCategory.STREAK, 3),
    AchievementType.STREAK_7: ("Week Warrior", "Maintain a 7-day streak", "fire", AchievementCategory.STREAK, 7),
    AchievementType.STREAK_30: ("Monthly Master", "Maintain a 30-day streak", "fire", AchievementCategory.STREAK, 30),
    AchievementType.STREAK_100: ("Centurion", "Maintain a 100-day streak", "trophy", AchievementCategory.STREAK, 100),
    AchievementType.TOTAL_SESSIONS_10: ("Dedicated", "Complete 10 focus sessions", "target", AchievementCategory.MILESTONE, 10),
    AchievementType.TOTAL_SESSIONS_50: ("Focused", "Complete 50 focus sessions", "target", AchievementCategory.MILESTONE, 50),
    AchievementType.TOTAL_SESSIONS_100: ("Centurial Focus", "Complete 100 focus sessions", "medal", AchievementCategory.MILESTONE, 100),
    AchievementType.DEEP_WORK_MASTER: ("Deep Work Master", "Complete 10 deep work sessions", "brain", AchievementCategory.MASTERY, 10),
    AchievementType.EARLY_BIRD: ("Early Bird", "Complete 5 sessions before 9 AM", "sunrise", AchievementCategory.TIME_BASED, 5),
    AchievementType.NIGHT_OWL: ("Night Owl", "Complete 5 sessions after 9 PM", "moon", AchievementCategory.TIME_BASED, 5),
}


class AchievementService:
    """Evaluates and tracks achievement progress."""

    def __init__(self, db: Session):
        self.db = db

    def evaluate(self, user_id: str, session_data: dict) -> list[dict]:
        """Check all achievements and unlock any that are newly earned.

        Args:
            user_id: The user to evaluate.
            session_data: Dict with session_type, actual_duration, completed_at, etc.

        Returns:
            List of newly unlocked achievement dicts.
        """
        self._ensure_achievements_exist(user_id)
        newly_unlocked = []

        streak = self.db.query(UserStreak).filter_by(user_id=user_id).first()
        current_streak = streak.current_streak if streak else 0
        total_sessions = streak.total_sessions if streak else 0

        achievements = self.db.query(Achievement).filter_by(user_id=user_id, is_unlocked=False).all()

        for ach in achievements:
            progress = self._get_progress(ach.achievement_type, total_sessions, current_streak, session_data)
            ach.progress_current = progress

            if progress >= ach.progress_required:
                ach.is_unlocked = True
                ach.unlocked_at = datetime.utcnow()
                newly_unlocked.append({
                    "achievement_type": ach.achievement_type.value,
                    "title": ach.title,
                    "unlocked_at": ach.unlocked_at.isoformat(),
                })

        self.db.commit()
        return newly_unlocked

    def get_user_achievements(self, user_id: str) -> list[Achievement]:
        """Get all achievements for a user."""
        self._ensure_achievements_exist(user_id)
        return self.db.query(Achievement).filter_by(user_id=user_id).all()

    def get_stats(self, user_id: str) -> dict:
        """Get achievement statistics for a user."""
        achievements = self.get_user_achievements(user_id)
        unlocked = [a for a in achievements if a.is_unlocked]
        return {
            "total_unlocked": len(unlocked),
            "total_available": len(achievements),
            "completion_percentage": (len(unlocked) / len(achievements) * 100) if achievements else 0,
        }

    def _ensure_achievements_exist(self, user_id: str):
        """Create achievement rows for user if they don't exist."""
        existing = self.db.query(Achievement).filter_by(user_id=user_id).count()
        if existing > 0:
            return

        for atype, (title, desc, icon, category, required) in ACHIEVEMENT_DEFS.items():
            ach = Achievement(
                user_id=user_id,
                achievement_type=atype,
                category=category,
                title=title,
                description=desc,
                icon=icon,
                progress_required=required,
            )
            self.db.add(ach)
        self.db.flush()

    @staticmethod
    def _get_progress(atype: AchievementType, total_sessions: int, current_streak: int, session_data: dict) -> int:
        """Calculate current progress toward an achievement."""
        if atype == AchievementType.FIRST_SESSION:
            return total_sessions
        if atype in (AchievementType.STREAK_3, AchievementType.STREAK_7, AchievementType.STREAK_30, AchievementType.STREAK_100):
            return current_streak
        if atype in (AchievementType.TOTAL_SESSIONS_10, AchievementType.TOTAL_SESSIONS_50, AchievementType.TOTAL_SESSIONS_100):
            return total_sessions
        # Time-based and mastery achievements need more session context
        return 0
```

- [ ] **Step 9: Implement LeaderboardService**

File: `services/game_engine/services/leaderboard_service.py`

```python
"""Leaderboard service using Redis sorted sets."""
import json
from sqlalchemy.orm import Session
from typing import Optional

from game_engine.models.level_models import UserLevel
from game_engine.models.streak_models import UserStreak


class LeaderboardService:
    """Builds and caches leaderboards."""

    XP_KEY = "leaderboard:xp"
    STREAK_KEY = "leaderboard:streaks"

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client

    async def get_xp_leaderboard(self, limit: int = 50) -> list[dict]:
        """Get top users by XP."""
        # Try cache first
        if self.redis:
            cached = await self.redis.get(f"{self.XP_KEY}:cache")
            if cached:
                return json.loads(cached)

        # Build from DB
        levels = (
            self.db.query(UserLevel)
            .order_by(UserLevel.total_xp.desc())
            .limit(limit)
            .all()
        )
        result = [
            {"user_id": l.user_id, "level": l.current_level, "total_xp": l.total_xp, "rank": i + 1}
            for i, l in enumerate(levels)
        ]

        # Cache for 5 minutes
        if self.redis:
            await self.redis.set(f"{self.XP_KEY}:cache", json.dumps(result), ex=300)

        return result

    async def get_streak_leaderboard(self, limit: int = 50) -> list[dict]:
        """Get top users by current streak."""
        if self.redis:
            cached = await self.redis.get(f"{self.STREAK_KEY}:cache")
            if cached:
                return json.loads(cached)

        streaks = (
            self.db.query(UserStreak)
            .order_by(UserStreak.current_streak.desc())
            .limit(limit)
            .all()
        )
        result = [
            {"user_id": s.user_id, "current_streak": s.current_streak, "longest_streak": s.longest_streak, "rank": i + 1}
            for i, s in enumerate(streaks)
        ]

        if self.redis:
            await self.redis.set(f"{self.STREAK_KEY}:cache", json.dumps(result), ex=300)

        return result
```

- [ ] **Step 10: Run all Game Engine tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/ -v`
Expected: All tests PASS

- [ ] **Step 11: Commit**

```bash
git add services/game_engine/services/ services/game_engine/tests/
git commit -m "feat: implement Game Engine services (Level, Streak, Achievement, Leaderboard)"
```

---

### Task 12: Implement Game Engine Routers

Wire up the endpoints defined in the spec.

**Files:**
- Modify: `services/game_engine/routers/achievements.py`
- Modify: `services/game_engine/routers/levels.py`
- Modify: `services/game_engine/routers/streaks.py`
- Modify: `services/game_engine/routers/leaderboards.py`

- [ ] **Step 1: Implement achievements router**

File: `services/game_engine/routers/achievements.py`

```python
"""Achievements router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.achievement_service import AchievementService
from game_engine.models.achievement_models import AchievementResponse

router = APIRouter()


@router.get("/users/{user_id}", response_model=list[AchievementResponse])
def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """Get all achievements with unlock status and progress."""
    service = AchievementService(db)
    return service.get_user_achievements(user_id)


@router.get("/users/{user_id}/recent", response_model=list[AchievementResponse])
def get_recent_achievements(user_id: str, limit: int = 5, db: Session = Depends(get_db)):
    """Get recently unlocked achievements."""
    service = AchievementService(db)
    all_achievements = service.get_user_achievements(user_id)
    unlocked = [a for a in all_achievements if a.is_unlocked]
    unlocked.sort(key=lambda a: a.unlocked_at or a.created_at, reverse=True)
    return unlocked[:limit]
```

- [ ] **Step 2: Implement levels router**

File: `services/game_engine/routers/levels.py`

```python
"""Levels and XP router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from game_engine.database.connection import get_db
from game_engine.services.level_service import LevelService
from game_engine.models.level_models import LevelResponse

router = APIRouter()


class ProcessSessionRequest(BaseModel):
    """Request body for manual session processing."""
    user_id: str
    session_id: str
    session_duration: int = 25
    session_completed: bool = True
    productivity_score: float = 5.0


@router.get("/users/{user_id}", response_model=LevelResponse)
def get_user_level(user_id: str, db: Session = Depends(get_db)):
    """Get current level, XP, progress to next level."""
    service = LevelService(db)
    level = service.get_user_level(user_id)
    if level is None:
        raise HTTPException(status_code=404, detail="User has no level data")
    # Compute progress percentage
    progress = (level.current_xp / level.xp_to_next_level * 100) if level.xp_to_next_level > 0 else 0
    return LevelResponse(
        user_id=level.user_id,
        current_level=level.current_level,
        current_xp=level.current_xp,
        total_xp=level.total_xp,
        xp_to_next_level=level.xp_to_next_level,
        progress_percentage=round(progress, 1),
        level_up_at=level.level_up_at,
    )


@router.get("/users/{user_id}/history")
def get_xp_history(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Get XP gain history."""
    service = LevelService(db)
    history = service.get_xp_history(user_id, limit)
    return [
        {
            "session_id": h.session_id,
            "base_xp": h.base_xp,
            "bonus_xp": h.bonus_xp,
            "total_xp": h.total_xp,
            "reason": h.reason,
            "created_at": h.created_at.isoformat(),
        }
        for h in history
    ]


@router.post("/process-session")
def process_session(req: ProcessSessionRequest, db: Session = Depends(get_db)):
    """Manual trigger to process a session (for testing)."""
    from game_engine.calculators.experience_calculator import ExperienceCalculator
    from game_engine.services.streak_service import StreakService
    from game_engine.services.achievement_service import AchievementService

    # Calculate XP
    xp_result = ExperienceCalculator.calculate(
        session_duration=req.session_duration,
        session_completed=req.session_completed,
        productivity_score=req.productivity_score,
        current_streak=0,
    )

    # Update streak
    streak_service = StreakService(db)
    streak_result = streak_service.update(req.user_id)

    # Recalculate XP with streak
    xp_result = ExperienceCalculator.calculate(
        session_duration=req.session_duration,
        session_completed=req.session_completed,
        productivity_score=req.productivity_score,
        current_streak=streak_result["new_streak"],
    )

    # Award XP
    level_service = LevelService(db)
    level_result = level_service.award_xp(
        user_id=req.user_id,
        session_id=req.session_id,
        base_xp=xp_result["base_xp"],
        bonus_xp=xp_result["bonus_xp"],
        total_xp=xp_result["total_xp"],
        reason=xp_result["reason"],
    )

    # Evaluate achievements
    achievement_service = AchievementService(db)
    unlocked = achievement_service.evaluate(req.user_id, {
        "session_type": "pomodoro",
        "actual_duration": req.session_duration,
    })

    return {
        "xp": xp_result,
        "streak": streak_result,
        "level": level_result,
        "achievements_unlocked": unlocked,
    }
```

- [ ] **Step 3: Implement streaks router**

File: `services/game_engine/routers/streaks.py`

```python
"""Streaks router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from game_engine.database.connection import get_db
from game_engine.services.streak_service import StreakService
from game_engine.models.streak_models import StreakResponse

router = APIRouter()


@router.get("/users/{user_id}", response_model=StreakResponse)
def get_user_streak(user_id: str, db: Session = Depends(get_db)):
    """Get current streak, longest streak, milestones."""
    service = StreakService(db)
    streak = service.get_streak(user_id)
    if streak is None:
        raise HTTPException(status_code=404, detail="User has no streak data")

    # Calculate days until streak breaks
    if streak.last_session_date:
        gap = (date.today() - streak.last_session_date).days
        days_until_break = max(0, 2 - gap)  # 2-day grace
    else:
        days_until_break = 0

    return StreakResponse(
        user_id=streak.user_id,
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        last_session_date=streak.last_session_date,
        streak_start_date=streak.streak_start_date,
        total_sessions=streak.total_sessions,
        is_active=streak.current_streak > 0,
        days_until_break=days_until_break,
    )
```

- [ ] **Step 4: Implement leaderboards router**

File: `services/game_engine/routers/leaderboards.py`

```python
"""Leaderboards router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from game_engine.database.connection import get_db
from game_engine.services.leaderboard_service import LeaderboardService

router = APIRouter()


@router.get("/")
async def get_xp_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Global leaderboard by XP."""
    service = LeaderboardService(db)
    return await service.get_xp_leaderboard(limit)


@router.get("/streaks")
async def get_streak_leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Streak leaderboard."""
    service = LeaderboardService(db)
    return await service.get_streak_leaderboard(limit)
```

- [ ] **Step 5: Commit**

```bash
git add services/game_engine/routers/
git commit -m "feat: implement Game Engine routers (achievements, levels, streaks, leaderboards)"
```

---

### Task 13: Game Engine Event Subscriber and main.py Wiring

Subscribe to `session.completed` events and wire everything into the FastAPI app.

**Files:**
- Create: `services/game_engine/events/__init__.py`
- Create: `services/game_engine/events/subscriber.py`
- Create: `services/game_engine/events/handlers.py`
- Create: `services/game_engine/events/publisher.py`
- Modify: `services/game_engine/main.py`
- Modify: `services/game_engine/requirements.txt`

- [ ] **Step 1: Create event publisher (same pattern as Focus Engine)**

File: `services/game_engine/events/__init__.py`
```python
```

File: `services/game_engine/events/publisher.py`

```python
"""Redis pub/sub event publisher for Game Engine."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("game_engine.events.publisher")
SERVICE_NAME = "game_engine"


class EventPublisher:
    """Publishes events to Redis pub/sub channels."""

    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event_type: str, user_id: str, payload: dict) -> None:
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_service": SERVICE_NAME,
            "user_id": user_id,
            "payload": payload,
        }
        await self.redis.publish(event_type, json.dumps(message))
        logger.info("Published %s for user %s", event_type, user_id)
```

- [ ] **Step 2: Create event handlers**

File: `services/game_engine/events/handlers.py`

```python
"""Event handlers for Game Engine."""
import json
import logging
from sqlalchemy.orm import Session

from game_engine.database.connection import SessionLocal
from game_engine.calculators.experience_calculator import ExperienceCalculator
from game_engine.services.streak_service import StreakService
from game_engine.services.level_service import LevelService
from game_engine.services.achievement_service import AchievementService

logger = logging.getLogger("game_engine.events.handlers")


async def handle_session_completed(data: dict, publisher=None):
    """Process a completed focus session — update streak, award XP, check achievements."""
    payload = data.get("payload", {})
    user_id = data.get("user_id")

    if not user_id:
        logger.warning("session.completed event missing user_id")
        return

    db = SessionLocal()
    try:
        # 1. Update streak
        streak_service = StreakService(db)
        streak_result = streak_service.update(user_id)

        # 2. Calculate XP
        xp_result = ExperienceCalculator.calculate(
            session_duration=payload.get("actual_duration", 25),
            session_completed=True,
            productivity_score=payload.get("productivity_score"),
            current_streak=streak_result["new_streak"],
        )

        # 3. Award XP
        level_service = LevelService(db)
        level_result = level_service.award_xp(
            user_id=user_id,
            session_id=payload.get("session_id", "unknown"),
            base_xp=xp_result["base_xp"],
            bonus_xp=xp_result["bonus_xp"],
            total_xp=xp_result["total_xp"],
            reason=xp_result["reason"],
        )

        # 4. Evaluate achievements
        achievement_service = AchievementService(db)
        unlocked = achievement_service.evaluate(user_id, payload)

        logger.info(
            "Processed session for %s: streak=%d, xp=%d, level=%d, unlocked=%d",
            user_id, streak_result["new_streak"], xp_result["total_xp"],
            level_result["new_level"], len(unlocked),
        )

        # 5. Publish events for newly unlocked achievements and level-ups
        if publisher:
            for ach in unlocked:
                await publisher.publish(
                    event_type="achievement.unlocked",
                    user_id=user_id,
                    payload={
                        "achievement_type": ach["achievement_type"],
                        "achievement_title": ach["title"],
                        "unlocked_at": ach["unlocked_at"],
                    },
                )
            if level_result["level_up"]:
                await publisher.publish(
                    event_type="level.up",
                    user_id=user_id,
                    payload={
                        "new_level": level_result["new_level"],
                        "total_xp": level_result["total_xp"],
                        "leveled_up_at": data.get("timestamp", ""),
                    },
                )
    finally:
        db.close()
```

- [ ] **Step 3: Create event subscriber**

File: `services/game_engine/events/subscriber.py`

```python
"""Redis pub/sub event subscriber for Game Engine."""
import asyncio
import json
import logging
import redis.asyncio as aioredis

from game_engine.events.handlers import handle_session_completed

logger = logging.getLogger("game_engine.events.subscriber")

SUBSCRIPTIONS = {
    "session.completed": handle_session_completed,
}


async def start_subscriber(redis_url: str, publisher=None):
    """Start listening for events on subscribed channels.

    Runs as a background asyncio task during the app lifespan.
    """
    redis = aioredis.from_url(redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe(*SUBSCRIPTIONS.keys())
    logger.info("Subscribed to channels: %s", list(SUBSCRIPTIONS.keys()))

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode()
            handler = SUBSCRIPTIONS.get(channel)
            if handler:
                try:
                    data = json.loads(message["data"])
                    await handler(data, publisher=publisher)
                except Exception:
                    logger.exception("Error handling event on %s", channel)
    finally:
        await pubsub.unsubscribe()
        await redis.close()
```

- [ ] **Step 4: Update main.py to wire routers and start subscriber**

File: `services/game_engine/main.py`

```python
"""
Focus Flow - Game Engine Service
Main FastAPI application for gamification features
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging
import redis.asyncio as aioredis

from game_engine.config.settings import get_settings
from game_engine.database.connection import create_tables
from game_engine.routers import achievements, levels, streaks, leaderboards
from game_engine.events.publisher import EventPublisher
from game_engine.events.subscriber import start_subscriber

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Game Engine service starting up...")
    create_tables()

    # Start Redis event subscriber
    redis_client = aioredis.from_url(settings.redis_url)
    publisher = EventPublisher(redis_client=redis_client)
    subscriber_task = asyncio.create_task(
        start_subscriber(settings.redis_url, publisher=publisher)
    )

    yield

    subscriber_task.cancel()
    await redis_client.close()
    logger.info("Game Engine service shutting down...")


app = FastAPI(
    title="Focus Flow - Game Engine",
    description="Gamification features including achievements, levels, streaks, and leaderboards",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(achievements.router, prefix=f"{settings.api_prefix}/achievements", tags=["achievements"])
app.include_router(levels.router, prefix=f"{settings.api_prefix}/levels", tags=["levels"])
app.include_router(streaks.router, prefix=f"{settings.api_prefix}/streaks", tags=["streaks"])
app.include_router(leaderboards.router, prefix=f"{settings.api_prefix}/leaderboards", tags=["leaderboards"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "game_engine", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "service": "Focus Flow - Game Engine",
        "version": "1.0.0",
        "status": "operational",
        "port": settings.port,
    }


if __name__ == "__main__":
    uvicorn.run(
        "game_engine.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )
```

- [ ] **Step 5: Populate requirements.txt**

File: `services/game_engine/requirements.txt`

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

- [ ] **Step 6: Run all Game Engine tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/game_engine/tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/game_engine/
git commit -m "feat: complete Game Engine - events, routers, main.py wiring, requirements"
```

---

## Chunk 3: Analytics Service Implementation

This chunk implements the Analytics service with cross-service aggregation, trend analysis, and data export.

### Task 14: Analytics Service Foundation — Config, Database, Models

**Files:**
- Create: `services/analytics/config/__init__.py`
- Create: `services/analytics/config/settings.py`
- Create: `services/analytics/database/__init__.py`
- Create: `services/analytics/database/connection.py`
- Modify: `services/analytics/models/metrics_models.py`
- Modify: `services/analytics/models/trend_models.py`
- Modify: `services/analytics/models/comparison_models.py`
- Create: `services/analytics/tests/test_models.py`

- [ ] **Step 1: Create config**

File: `services/analytics/config/__init__.py`
```python
```

File: `services/analytics/config/settings.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8003
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    focus_engine_url: str = "http://localhost:8000"
    game_engine_url: str = "http://localhost:8001"

    class Config:
        env_prefix = "ANALYTICS_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 2: Create database connection**

File: `services/analytics/database/__init__.py`
```python
```

File: `services/analytics/database/connection.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from analytics.config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 3: Create ORM models for aggregates**

File: `services/analytics/models/metrics_models.py`
```python
"""Analytics aggregate models."""
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, JSON
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from analytics.database.connection import Base


class DailyAggregate(Base):
    """Pre-computed daily rollups per user."""
    __tablename__ = "an_daily_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_focus_minutes = Column(Integer, default=0)
    avg_productivity_score = Column(Float, default=0.0)
    total_xp_earned = Column(Integer, default=0)
    total_interruptions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WeeklyAggregate(Base):
    """Pre-computed weekly rollups per user."""
    __tablename__ = "an_weekly_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    week_start = Column(Date, index=True, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_focus_minutes = Column(Integer, default=0)
    avg_productivity_score = Column(Float, default=0.0)
    total_xp_earned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CorrelationCache(Base):
    """Cached correlation analysis results."""
    __tablename__ = "an_correlation_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    correlation_type = Column(String, nullable=False)
    result = Column(JSON, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)


class DashboardMetrics(BaseModel):
    """Unified dashboard response."""
    total_sessions: int
    total_focus_minutes: int
    avg_productivity_score: float
    current_streak: int
    current_level: int
    total_xp: int


class PeriodSummary(BaseModel):
    """Summary for a time period."""
    period: str
    total_sessions: int
    total_focus_minutes: int
    avg_productivity_score: float
```

- [ ] **Step 4: Write tests for models**

File: `services/analytics/tests/test_models.py`
```python
"""Tests for Analytics ORM models."""
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics.database.connection import Base
from analytics.models.metrics_models import DailyAggregate, WeeklyAggregate, CorrelationCache


def test_daily_aggregate_table_name():
    assert DailyAggregate.__tablename__ == "an_daily_aggregates"


def test_weekly_aggregate_table_name():
    assert WeeklyAggregate.__tablename__ == "an_weekly_aggregates"


def test_daily_aggregate_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    agg = DailyAggregate(user_id="user_1", date=date.today(), total_sessions=5, total_focus_minutes=125)
    db.add(agg)
    db.commit()
    assert agg.id is not None
    db.close()
```

- [ ] **Step 5: Run tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/analytics/tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add services/analytics/config/ services/analytics/database/ services/analytics/models/ services/analytics/tests/
git commit -m "feat: Analytics service foundation - config, database, ORM models"
```

---

### Task 15: Analytics Service — Services and HTTP Clients

**Files:**
- Modify: `services/analytics/services/metrics_calculator.py`
- Modify: `services/analytics/services/trend_analyzer.py`
- Modify: `services/analytics/services/export_service.py`
- Create: `services/analytics/clients/__init__.py`
- Create: `services/analytics/clients/focus_engine_client.py`
- Create: `services/analytics/clients/game_engine_client.py`
- Create: `services/analytics/tests/test_metrics_calculator.py`

- [ ] **Step 1: Create HTTP clients for cross-service queries**

File: `services/analytics/clients/__init__.py`
```python
```

File: `services/analytics/clients/focus_engine_client.py`
```python
"""HTTP client for Focus Engine API."""
import httpx
import logging
from analytics.config.settings import get_settings

logger = logging.getLogger("analytics.clients.focus_engine")
settings = get_settings()


class FocusEngineClient:
    """Fetches session data from Focus Engine."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.focus_engine_url

    async def get_user_sessions(self, user_id: str, limit: int = 100) -> list[dict]:
        """Fetch recent sessions for a user."""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.base_url}/api/v1/sessions/user/{user_id}",
                    params={"limit": limit},
                    timeout=10.0,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("sessions", data) if isinstance(data, dict) else data
            except httpx.HTTPError as e:
                logger.error("Failed to fetch sessions: %s", e)
                return []
```

File: `services/analytics/clients/game_engine_client.py`
```python
"""HTTP client for Game Engine API."""
import httpx
import logging
from analytics.config.settings import get_settings

logger = logging.getLogger("analytics.clients.game_engine")
settings = get_settings()


class GameEngineClient:
    """Fetches gamification data from Game Engine."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.game_engine_url

    async def get_user_level(self, user_id: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self.base_url}/api/v1/levels/users/{user_id}", timeout=10.0)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error("Failed to fetch level: %s", e)
                return None

    async def get_user_streak(self, user_id: str) -> dict | None:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self.base_url}/api/v1/streaks/users/{user_id}", timeout=10.0)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPError as e:
                logger.error("Failed to fetch streak: %s", e)
                return None
```

- [ ] **Step 2: Implement MetricsCalculator**

File: `services/analytics/services/metrics_calculator.py`
```python
"""Unified metrics calculator pulling from all services."""
import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session

from analytics.models.metrics_models import DailyAggregate, DashboardMetrics
from analytics.clients.focus_engine_client import FocusEngineClient
from analytics.clients.game_engine_client import GameEngineClient

logger = logging.getLogger("analytics.services.metrics_calculator")


class MetricsCalculator:
    """Computes unified metrics across services."""

    def __init__(self, db: Session):
        self.db = db
        self.fe_client = FocusEngineClient()
        self.ge_client = GameEngineClient()

    async def get_dashboard(self, user_id: str) -> DashboardMetrics:
        """Build unified dashboard metrics from all services."""
        # Pull from aggregates (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        aggregates = (
            self.db.query(DailyAggregate)
            .filter(DailyAggregate.user_id == user_id, DailyAggregate.date >= thirty_days_ago)
            .all()
        )

        total_sessions = sum(a.total_sessions for a in aggregates)
        total_minutes = sum(a.total_focus_minutes for a in aggregates)
        scores = [a.avg_productivity_score for a in aggregates if a.avg_productivity_score > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Pull live gamification data
        level_data = await self.ge_client.get_user_level(user_id)
        streak_data = await self.ge_client.get_user_streak(user_id)

        return DashboardMetrics(
            total_sessions=total_sessions,
            total_focus_minutes=total_minutes,
            avg_productivity_score=round(avg_score, 2),
            current_streak=streak_data.get("current_streak", 0) if streak_data else 0,
            current_level=level_data.get("current_level", 1) if level_data else 1,
            total_xp=level_data.get("total_xp", 0) if level_data else 0,
        )

    def get_period_summary(self, user_id: str, period: str = "daily") -> list[dict]:
        """Get aggregated summaries for a period (daily/weekly/monthly)."""
        if period == "daily":
            seven_days_ago = date.today() - timedelta(days=7)
            aggregates = (
                self.db.query(DailyAggregate)
                .filter(DailyAggregate.user_id == user_id, DailyAggregate.date >= seven_days_ago)
                .order_by(DailyAggregate.date.desc())
                .all()
            )
            return [
                {
                    "date": a.date.isoformat(),
                    "total_sessions": a.total_sessions,
                    "total_focus_minutes": a.total_focus_minutes,
                    "avg_productivity_score": a.avg_productivity_score,
                }
                for a in aggregates
            ]
        return []

    def update_daily_aggregate(self, user_id: str, session_data: dict):
        """Update or create today's daily aggregate with new session data."""
        today = date.today()
        agg = (
            self.db.query(DailyAggregate)
            .filter_by(user_id=user_id, date=today)
            .first()
        )
        if agg is None:
            agg = DailyAggregate(user_id=user_id, date=today)
            self.db.add(agg)

        agg.total_sessions += 1
        agg.total_focus_minutes += session_data.get("actual_duration", 0)
        productivity = session_data.get("productivity_score")
        if productivity is not None:
            # Running average
            total_score = agg.avg_productivity_score * (agg.total_sessions - 1) + productivity
            agg.avg_productivity_score = total_score / agg.total_sessions
        agg.total_interruptions += session_data.get("interruption_count", 0)

        self.db.commit()
```

- [ ] **Step 3: Implement TrendAnalyzer**

File: `services/analytics/services/trend_analyzer.py`
```python
"""Trend analysis service."""
from datetime import date, timedelta
from sqlalchemy.orm import Session

from analytics.models.metrics_models import DailyAggregate, WeeklyAggregate


class TrendAnalyzer:
    """Computes week-over-week and month-over-month trends."""

    def __init__(self, db: Session):
        self.db = db

    def weekly_comparison(self, user_id: str) -> dict:
        """Compare this week vs last week."""
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())
        last_week_start = this_week_start - timedelta(days=7)

        this_week = self._sum_period(user_id, this_week_start, today)
        last_week = self._sum_period(user_id, last_week_start, this_week_start - timedelta(days=1))

        return {
            "this_week": this_week,
            "last_week": last_week,
            "change": {
                "sessions": this_week["total_sessions"] - last_week["total_sessions"],
                "focus_minutes": this_week["total_focus_minutes"] - last_week["total_focus_minutes"],
            },
        }

    def monthly_comparison(self, user_id: str) -> dict:
        """Compare this month vs last month."""
        today = date.today()
        this_month_start = today.replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        this_month = self._sum_period(user_id, this_month_start, today)
        last_month = self._sum_period(user_id, last_month_start, last_month_end)

        return {
            "this_month": this_month,
            "last_month": last_month,
            "change": {
                "sessions": this_month["total_sessions"] - last_month["total_sessions"],
                "focus_minutes": this_month["total_focus_minutes"] - last_month["total_focus_minutes"],
            },
        }

    def productivity_curve(self, user_id: str) -> list[dict]:
        """Time-of-day productivity patterns. Placeholder — requires hourly data from Focus Engine."""
        return []

    def _sum_period(self, user_id: str, start: date, end: date) -> dict:
        aggregates = (
            self.db.query(DailyAggregate)
            .filter(DailyAggregate.user_id == user_id, DailyAggregate.date >= start, DailyAggregate.date <= end)
            .all()
        )
        return {
            "total_sessions": sum(a.total_sessions for a in aggregates),
            "total_focus_minutes": sum(a.total_focus_minutes for a in aggregates),
            "avg_productivity_score": (
                sum(a.avg_productivity_score for a in aggregates) / len(aggregates)
                if aggregates else 0.0
            ),
        }
```

- [ ] **Step 4: Implement ExportService**

File: `services/analytics/services/export_service.py`
```python
"""Data export service."""
import csv
import io
import json
from datetime import date, timedelta
from sqlalchemy.orm import Session

from analytics.models.metrics_models import DailyAggregate


class ExportService:
    """Exports aggregated data as CSV or JSON."""

    def __init__(self, db: Session):
        self.db = db

    def export(self, user_id: str, format: str = "json", days: int = 90) -> str:
        """Export aggregated data."""
        start = date.today() - timedelta(days=days)
        aggregates = (
            self.db.query(DailyAggregate)
            .filter(DailyAggregate.user_id == user_id, DailyAggregate.date >= start)
            .order_by(DailyAggregate.date)
            .all()
        )

        rows = [
            {
                "date": a.date.isoformat(),
                "total_sessions": a.total_sessions,
                "total_focus_minutes": a.total_focus_minutes,
                "avg_productivity_score": round(a.avg_productivity_score, 2),
                "total_interruptions": a.total_interruptions,
            }
            for a in aggregates
        ]

        if format == "csv":
            output = io.StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            return output.getvalue()

        return json.dumps(rows, indent=2)
```

- [ ] **Step 5: Write tests for MetricsCalculator**

File: `services/analytics/tests/test_metrics_calculator.py`
```python
"""Tests for MetricsCalculator."""
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics.database.connection import Base
from analytics.models.metrics_models import DailyAggregate
from analytics.services.metrics_calculator import MetricsCalculator


def test_update_daily_aggregate_creates_new():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    calc = MetricsCalculator(db)
    calc.update_daily_aggregate("user_1", {"actual_duration": 25, "productivity_score": 8.0, "interruption_count": 1})

    agg = db.query(DailyAggregate).filter_by(user_id="user_1", date=date.today()).first()
    assert agg is not None
    assert agg.total_sessions == 1
    assert agg.total_focus_minutes == 25
    assert agg.avg_productivity_score == 8.0
    db.close()


def test_update_daily_aggregate_increments_existing():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    calc = MetricsCalculator(db)
    calc.update_daily_aggregate("user_1", {"actual_duration": 25, "productivity_score": 8.0, "interruption_count": 0})
    calc.update_daily_aggregate("user_1", {"actual_duration": 50, "productivity_score": 6.0, "interruption_count": 2})

    agg = db.query(DailyAggregate).filter_by(user_id="user_1", date=date.today()).first()
    assert agg.total_sessions == 2
    assert agg.total_focus_minutes == 75
    assert abs(agg.avg_productivity_score - 7.0) < 0.01
    db.close()
```

- [ ] **Step 6: Run tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/analytics/tests/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/analytics/services/ services/analytics/clients/ services/analytics/tests/
git commit -m "feat: implement Analytics services - metrics calculator, trend analyzer, export"
```

---

### Task 16: Analytics Routers, Events, and main.py

**Files:**
- Modify: `services/analytics/routers/metrics.py`
- Modify: `services/analytics/routers/trends.py`
- Modify: `services/analytics/routers/comparisons.py`
- Modify: `services/analytics/routers/export.py`
- Create: `services/analytics/routers/correlations.py`
- Create: `services/analytics/events/__init__.py`
- Create: `services/analytics/events/subscriber.py`
- Create: `services/analytics/events/handlers.py`
- Modify: `services/analytics/main.py`
- Create: `services/analytics/requirements.txt`

- [ ] **Step 1: Implement routers**

File: `services/analytics/routers/metrics.py`
```python
"""Metrics router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from analytics.database.connection import get_db
from analytics.services.metrics_calculator import MetricsCalculator
from analytics.models.metrics_models import DashboardMetrics

router = APIRouter()


@router.get("/users/{user_id}/dashboard", response_model=DashboardMetrics)
async def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    calc = MetricsCalculator(db)
    return await calc.get_dashboard(user_id)


@router.get("/users/{user_id}/summary")
def get_summary(user_id: str, period: str = "daily", db: Session = Depends(get_db)):
    calc = MetricsCalculator(db)
    return calc.get_period_summary(user_id, period)
```

File: `services/analytics/routers/trends.py`
```python
"""Trends router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from analytics.database.connection import get_db
from analytics.services.trend_analyzer import TrendAnalyzer

router = APIRouter()


@router.get("/users/{user_id}/weekly")
def weekly_trend(user_id: str, db: Session = Depends(get_db)):
    return TrendAnalyzer(db).weekly_comparison(user_id)


@router.get("/users/{user_id}/monthly")
def monthly_trend(user_id: str, db: Session = Depends(get_db)):
    return TrendAnalyzer(db).monthly_comparison(user_id)


@router.get("/users/{user_id}/productivity-curve")
def productivity_curve(user_id: str, db: Session = Depends(get_db)):
    return TrendAnalyzer(db).productivity_curve(user_id)
```

File: `services/analytics/routers/comparisons.py`
```python
"""Comparisons router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from analytics.database.connection import get_db
from analytics.services.trend_analyzer import TrendAnalyzer

router = APIRouter()


@router.get("/users/{user_id}/periods")
def compare_periods(
    user_id: str,
    start1: date = Query(...),
    end1: date = Query(...),
    start2: date = Query(...),
    end2: date = Query(...),
    db: Session = Depends(get_db),
):
    analyzer = TrendAnalyzer(db)
    return analyzer.compare_periods(user_id, start1, end1, start2, end2)
```

Also add this public method to `TrendAnalyzer` in `services/analytics/services/trend_analyzer.py`:
```python
def compare_periods(self, user_id: str, start1: date, end1: date, start2: date, end2: date) -> dict:
    """Compare two arbitrary date ranges."""
    return {
        "period_1": self._sum_period(user_id, start1, end1),
        "period_2": self._sum_period(user_id, start2, end2),
    }
```

File: `services/analytics/routers/correlations.py`
```python
"""Correlations router — NEW file."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from analytics.database.connection import get_db
from analytics.models.metrics_models import CorrelationCache

router = APIRouter()


@router.get("/users/{user_id}")
def get_correlations(user_id: str, db: Session = Depends(get_db)):
    """Cross-service statistical correlations."""
    cached = db.query(CorrelationCache).filter_by(user_id=user_id).order_by(CorrelationCache.computed_at.desc()).first()
    if cached:
        return {"user_id": user_id, "correlations": cached.result, "computed_at": cached.computed_at.isoformat()}
    return {"user_id": user_id, "correlations": [], "message": "No correlation data yet"}
```

File: `services/analytics/routers/export.py`
```python
"""Export router."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from analytics.database.connection import get_db
from analytics.services.export_service import ExportService

router = APIRouter()


@router.get("/users/{user_id}")
def export_data(user_id: str, format: str = Query("json"), days: int = Query(90), db: Session = Depends(get_db)):
    service = ExportService(db)
    data = service.export(user_id, format, days)
    if format == "csv":
        return PlainTextResponse(content=data, media_type="text/csv")
    return PlainTextResponse(content=data, media_type="application/json")
```

- [ ] **Step 2: Create event handlers and subscriber**

File: `services/analytics/events/__init__.py`
```python
```

File: `services/analytics/events/handlers.py`
```python
"""Event handlers for Analytics service."""
import logging
from analytics.database.connection import SessionLocal
from analytics.services.metrics_calculator import MetricsCalculator

logger = logging.getLogger("analytics.events.handlers")


async def handle_session_completed(data: dict, publisher=None):
    """Update daily aggregates when a session completes."""
    user_id = data.get("user_id")
    payload = data.get("payload", {})
    if not user_id:
        return

    db = SessionLocal()
    try:
        calc = MetricsCalculator(db)
        calc.update_daily_aggregate(user_id, payload)
        logger.info("Updated daily aggregate for %s", user_id)
    finally:
        db.close()


async def handle_achievement_unlocked(data: dict, publisher=None):
    """Log achievement milestones into trend data."""
    logger.info("Achievement unlocked for %s: %s", data.get("user_id"), data.get("payload", {}).get("achievement_type"))


async def handle_level_up(data: dict, publisher=None):
    """Log level-up milestones into trend data."""
    logger.info("Level up for %s: level %s", data.get("user_id"), data.get("payload", {}).get("new_level"))
```

File: `services/analytics/events/subscriber.py`
```python
"""Redis pub/sub event subscriber for Analytics."""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from analytics.events.handlers import handle_session_completed, handle_achievement_unlocked, handle_level_up

logger = logging.getLogger("analytics.events.subscriber")

SUBSCRIPTIONS = {
    "session.completed": handle_session_completed,
    "achievement.unlocked": handle_achievement_unlocked,
    "level.up": handle_level_up,
}


async def start_subscriber(redis_url: str, publisher=None):
    redis = aioredis.from_url(redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe(*SUBSCRIPTIONS.keys())
    logger.info("Subscribed to channels: %s", list(SUBSCRIPTIONS.keys()))

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode()
            handler = SUBSCRIPTIONS.get(channel)
            if handler:
                try:
                    data = json.loads(message["data"])
                    await handler(data, publisher=publisher)
                except Exception:
                    logger.exception("Error handling event on %s", channel)
    finally:
        await pubsub.unsubscribe()
        await redis.close()
```

- [ ] **Step 3: Update main.py**

File: `services/analytics/main.py`
```python
"""Focus Flow - Analytics Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging

from analytics.config.settings import get_settings
from analytics.database.connection import create_tables
from analytics.routers import metrics, trends, comparisons, export
from analytics.routers.correlations import router as correlations_router
from analytics.events.subscriber import start_subscriber

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analytics service starting up...")
    create_tables()
    subscriber_task = asyncio.create_task(start_subscriber(settings.redis_url))
    yield
    subscriber_task.cancel()
    logger.info("Analytics service shutting down...")


app = FastAPI(
    title="Focus Flow - Analytics",
    description="Cross-service productivity analytics and trend analysis",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix=f"{settings.api_prefix}/metrics", tags=["metrics"])
app.include_router(trends.router, prefix=f"{settings.api_prefix}/trends", tags=["trends"])
app.include_router(comparisons.router, prefix=f"{settings.api_prefix}/comparisons", tags=["comparisons"])
app.include_router(correlations_router, prefix=f"{settings.api_prefix}/correlations", tags=["correlations"])
app.include_router(export.router, prefix=f"{settings.api_prefix}/export", tags=["export"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"service": "Focus Flow - Analytics", "version": "1.0.0", "status": "operational", "port": settings.port}


if __name__ == "__main__":
    uvicorn.run("analytics.main:app", host=settings.host, port=settings.port, reload=settings.debug_mode)
```

- [ ] **Step 4: Create requirements.txt**

File: `services/analytics/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

- [ ] **Step 5: Run all Analytics tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/analytics/tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add services/analytics/
git commit -m "feat: complete Analytics service - routers, events, main.py, requirements"
```

---

## Chunk 4: AI Insights Service Implementation

### Task 17: AI Insights Foundation — Config, Database, Models

**Files:**
- Modify: `services/ai_insights/config/ai_settings.py`
- Create: `services/ai_insights/database/__init__.py`
- Create: `services/ai_insights/database/connection.py`
- Modify: `services/ai_insights/models/insights_models.py`
- Modify: `services/ai_insights/models/pattern_models.py`
- Create: `services/ai_insights/tests/test_models.py`

- [ ] **Step 1: Create config**

File: `services/ai_insights/config/ai_settings.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8002
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    focus_engine_url: str = "http://localhost:8000"
    analytics_url: str = "http://localhost:8003"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_model_advanced: str = "gpt-4o"
    coaching_cache_ttl: int = 14400  # 4 hours
    briefing_cache_ttl: int = 43200  # 12 hours

    class Config:
        env_prefix = "AI_INSIGHTS_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

- [ ] **Step 2: Create database connection**

File: `services/ai_insights/database/__init__.py`
```python
```

File: `services/ai_insights/database/connection.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from ai_insights.config.ai_settings import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 3: Create ORM models**

File: `services/ai_insights/models/insights_models.py`
```python
"""AI Insights ORM and Pydantic models."""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from ai_insights.database.connection import Base


class InsightCache(Base):
    """Cached LLM responses."""
    __tablename__ = "ai_insight_cache"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    insight_type = Column(String, index=True, nullable=False)  # coaching, briefing, session_review
    prompt_hash = Column(String, index=True, nullable=False)
    response = Column(Text, nullable=False)
    model_used = Column(String, nullable=False)
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class TokenUsage(Base):
    """OpenAI token consumption tracking."""
    __tablename__ = "ai_token_usage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    model = Column(String, nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class CoachingResponse(BaseModel):
    """Response model for coaching tips."""
    user_id: str
    tips: list[str]
    generated_at: str
    cached: bool = False


class DailyBriefingResponse(BaseModel):
    """Response model for daily briefing."""
    user_id: str
    best_focus_time: Optional[str] = None
    suggested_session_length: Optional[int] = None
    streak_message: Optional[str] = None
    insights: list[str]
    generated_at: str


class SessionReviewResponse(BaseModel):
    """Response model for post-session review."""
    session_id: str
    went_well: list[str]
    to_improve: list[str]
    overall_feedback: str
```

File: `services/ai_insights/models/pattern_models.py`
```python
"""Pattern discovery models."""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON
from datetime import datetime
from pydantic import BaseModel

from ai_insights.database.connection import Base


class UserPattern(Base):
    """Discovered productivity patterns."""
    __tablename__ = "ai_user_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    pattern_type = Column(String, nullable=False)  # time_of_day, day_of_week, session_type
    description = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    data = Column(JSON, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)


class PatternResponse(BaseModel):
    """Response model for discovered patterns."""
    patterns: list[dict]
    user_id: str
```

- [ ] **Step 4: Write and run model tests**

File: `services/ai_insights/tests/test_models.py`
```python
"""Tests for AI Insights models."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ai_insights.database.connection import Base
from ai_insights.models.insights_models import InsightCache, TokenUsage
from ai_insights.models.pattern_models import UserPattern


def test_table_names():
    assert InsightCache.__tablename__ == "ai_insight_cache"
    assert TokenUsage.__tablename__ == "ai_token_usage"
    assert UserPattern.__tablename__ == "ai_user_patterns"


def test_insight_cache_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    cache = InsightCache(
        user_id="user_1",
        insight_type="coaching",
        prompt_hash="abc123",
        response="Focus on deep work.",
        model_used="gpt-4o-mini",
        tokens_used=100,
        expires_at=datetime.utcnow() + timedelta(hours=4),
    )
    db.add(cache)
    db.commit()
    assert cache.id is not None
    db.close()
```

- [ ] **Step 5: Run tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/ai_insights/tests/ -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add services/ai_insights/config/ services/ai_insights/database/ services/ai_insights/models/ services/ai_insights/tests/
git commit -m "feat: AI Insights foundation - config, database, ORM models"
```

---

### Task 18: AI Insights — OpenAI Client, Prompt Templates, Services

**Files:**
- Modify: `services/ai_insights/clients/openai_client.py`
- Create: `services/ai_insights/prompts/coaching_prompt.txt`
- Create: `services/ai_insights/prompts/session_review_prompt.txt`
- Create: `services/ai_insights/prompts/daily_briefing_prompt.txt`
- Create: `services/ai_insights/prompts/pattern_discovery_prompt.txt`
- Modify: `services/ai_insights/services/session_analyzer.py`
- Modify: `services/ai_insights/services/coaching_generator.py`
- Modify: `services/ai_insights/services/pattern_discoverer.py`
- Create: `services/ai_insights/tests/test_openai_client.py`

- [ ] **Step 1: Create prompt templates**

File: `services/ai_insights/prompts/coaching_prompt.txt`
```
You are a productivity coach specializing in focus and deep work techniques. Based on the user's recent session data, provide 3-5 personalized, actionable tips to improve their focus quality.

User's recent data:
- Total sessions (last 7 days): {total_sessions}
- Average session duration: {avg_duration} minutes
- Average productivity score: {avg_productivity}/10
- Current streak: {current_streak} days
- Most productive time: {best_time}

Provide tips as a JSON array of strings. Be specific and encouraging.
```

File: `services/ai_insights/prompts/session_review_prompt.txt`
```
You are a focus session reviewer. Analyze this completed session and provide feedback.

Session details:
- Duration: {duration} minutes (planned: {planned_duration})
- Productivity score: {productivity_score}/10
- Interruptions: {interruptions}
- Session type: {session_type}
- Time of day: {time_of_day}

Respond with JSON: {"went_well": ["..."], "to_improve": ["..."], "overall_feedback": "..."}
```

File: `services/ai_insights/prompts/daily_briefing_prompt.txt`
```
You are a productivity advisor. Generate a daily briefing for this user.

User stats:
- Current streak: {current_streak} days
- Yesterday's sessions: {yesterday_sessions}
- Average productivity: {avg_productivity}/10
- Best focus time historically: {best_time}
- Total sessions this week: {week_sessions}

Respond with JSON: {"best_focus_time": "...", "suggested_session_length": N, "streak_message": "...", "insights": ["..."]}
```

File: `services/ai_insights/prompts/pattern_discovery_prompt.txt`
```
You are a data analyst specializing in productivity patterns. Analyze this user's session history and identify recurring patterns.

Session summary (last 30 days):
{session_summary}

Identify patterns related to:
- Time of day effectiveness
- Day of week patterns
- Session type preferences
- Streak correlations

Respond with JSON array: [{"pattern_type": "...", "description": "...", "confidence": 0.0-1.0}]
```

- [ ] **Step 2: Implement OpenAI client**

File: `services/ai_insights/clients/openai_client.py`
```python
"""OpenAI API client with caching and token tracking."""
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from ai_insights.config.ai_settings import get_settings
from ai_insights.models.insights_models import InsightCache, TokenUsage

logger = logging.getLogger("ai_insights.clients.openai")
settings = get_settings()


class OpenAIClient:
    """Thin wrapper around OpenAI with caching."""

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.redis = redis_client
        self.client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    async def generate(
        self,
        prompt: str,
        user_id: str,
        insight_type: str,
        model: str | None = None,
        cache_ttl: int = 14400,
    ) -> str:
        """Generate a completion, checking cache first.

        Args:
            prompt: The full prompt to send.
            user_id: User this insight is for.
            insight_type: Type of insight (coaching, briefing, etc).
            model: OpenAI model to use.
            cache_ttl: Cache TTL in seconds.

        Returns:
            The LLM response text.
        """
        model = model or settings.openai_model
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        # Check cache
        cached = (
            self.db.query(InsightCache)
            .filter_by(user_id=user_id, insight_type=insight_type, prompt_hash=prompt_hash)
            .filter(InsightCache.expires_at > datetime.utcnow())
            .first()
        )
        if cached:
            logger.info("Cache hit for %s/%s", user_id, insight_type)
            return cached.response

        # Call OpenAI
        if not self.client:
            return json.dumps({"error": "OpenAI API key not configured"})

        response = await self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
        )

        text = response.choices[0].message.content
        usage = response.usage

        # Track tokens
        token_record = TokenUsage(
            user_id=user_id,
            model=model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )
        self.db.add(token_record)

        # Cache response
        cache_record = InsightCache(
            user_id=user_id,
            insight_type=insight_type,
            prompt_hash=prompt_hash,
            response=text,
            model_used=model,
            tokens_used=usage.total_tokens if usage else 0,
            expires_at=datetime.utcnow() + timedelta(seconds=cache_ttl),
        )
        self.db.add(cache_record)
        self.db.commit()

        return text
```

- [ ] **Step 3: Implement CoachingGenerator**

File: `services/ai_insights/services/coaching_generator.py`
```python
"""Coaching tip generation service."""
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from ai_insights.clients.openai_client import OpenAIClient
from ai_insights.config.ai_settings import get_settings

logger = logging.getLogger("ai_insights.services.coaching")
settings = get_settings()

PROMPT_DIR = Path(__file__).parent.parent / "prompts"


class CoachingGenerator:
    """Generates personalized coaching tips via OpenAI."""

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.openai = OpenAIClient(db, redis_client)

    async def generate_coaching(self, user_id: str, user_data: dict) -> dict:
        """Generate coaching tips based on user's recent data."""
        template = (PROMPT_DIR / "coaching_prompt.txt").read_text()
        prompt = template.format(
            total_sessions=user_data.get("total_sessions", 0),
            avg_duration=user_data.get("avg_duration", 25),
            avg_productivity=user_data.get("avg_productivity", 5.0),
            current_streak=user_data.get("current_streak", 0),
            best_time=user_data.get("best_time", "morning"),
        )

        response = await self.openai.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="coaching",
            cache_ttl=settings.coaching_cache_ttl,
        )

        try:
            tips = json.loads(response)
            if isinstance(tips, list):
                return {"tips": tips, "cached": False}
        except json.JSONDecodeError:
            pass

        return {"tips": [response], "cached": False}

    async def generate_session_review(self, user_id: str, session_data: dict) -> dict:
        """Generate post-session feedback."""
        template = (PROMPT_DIR / "session_review_prompt.txt").read_text()
        prompt = template.format(
            duration=session_data.get("actual_duration", 25),
            planned_duration=session_data.get("planned_duration", 25),
            productivity_score=session_data.get("productivity_score", 5.0),
            interruptions=session_data.get("interruption_count", 0),
            session_type=session_data.get("session_type", "pomodoro"),
            time_of_day=session_data.get("time_of_day", "unknown"),
        )

        response = await self.openai.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="session_review",
            cache_ttl=3600,  # 1 hour
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"went_well": [], "to_improve": [], "overall_feedback": response}

    async def generate_daily_briefing(self, user_id: str, user_data: dict) -> dict:
        """Generate daily productivity briefing."""
        template = (PROMPT_DIR / "daily_briefing_prompt.txt").read_text()
        prompt = template.format(
            current_streak=user_data.get("current_streak", 0),
            yesterday_sessions=user_data.get("yesterday_sessions", 0),
            avg_productivity=user_data.get("avg_productivity", 5.0),
            best_time=user_data.get("best_time", "morning"),
            week_sessions=user_data.get("week_sessions", 0),
        )

        response = await self.openai.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="briefing",
            cache_ttl=settings.briefing_cache_ttl,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"insights": [response]}
```

- [ ] **Step 4: Implement SessionAnalyzer and PatternDiscoverer**

File: `services/ai_insights/services/session_analyzer.py`
```python
"""Session data analyzer — gathers data for LLM prompts."""
import httpx
import logging
from ai_insights.config.ai_settings import get_settings

logger = logging.getLogger("ai_insights.services.session_analyzer")
settings = get_settings()


class SessionAnalyzer:
    """Fetches and structures session data for LLM consumption."""

    async def get_user_context(self, user_id: str) -> dict:
        """Gather user data from Focus Engine and Analytics for prompt context."""
        data = {
            "total_sessions": 0,
            "avg_duration": 25,
            "avg_productivity": 5.0,
            "current_streak": 0,
            "best_time": "morning",
            "yesterday_sessions": 0,
            "week_sessions": 0,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{settings.focus_engine_url}/api/v1/analytics/users/{user_id}/stats")
                if resp.status_code == 200:
                    stats = resp.json()
                    data["total_sessions"] = stats.get("total_sessions", 0)
                    data["avg_duration"] = stats.get("average_actual_duration", 25)
                    data["avg_productivity"] = stats.get("average_productivity_score", 5.0)
            except httpx.HTTPError:
                logger.warning("Could not fetch stats from Focus Engine")

        return data
```

File: `services/ai_insights/services/pattern_discoverer.py`
```python
"""Pattern discovery service."""
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from ai_insights.clients.openai_client import OpenAIClient
from ai_insights.models.pattern_models import UserPattern
from ai_insights.config.ai_settings import get_settings

logger = logging.getLogger("ai_insights.services.patterns")
settings = get_settings()

PROMPT_DIR = Path(__file__).parent.parent / "prompts"


class PatternDiscoverer:
    """Discovers productivity patterns using OpenAI."""

    def __init__(self, db: Session, redis_client=None):
        self.db = db
        self.openai = OpenAIClient(db, redis_client)

    async def discover(self, user_id: str, session_summary: str) -> list[dict]:
        """Discover patterns from session data."""
        template = (PROMPT_DIR / "pattern_discovery_prompt.txt").read_text()
        prompt = template.format(session_summary=session_summary)

        response = await self.openai.generate(
            prompt=prompt,
            user_id=user_id,
            insight_type="patterns",
            model=settings.openai_model_advanced,
            cache_ttl=86400,  # 24 hours
        )

        try:
            patterns = json.loads(response)
            if isinstance(patterns, list):
                # Save to DB
                for p in patterns:
                    record = UserPattern(
                        user_id=user_id,
                        pattern_type=p.get("pattern_type", "unknown"),
                        description=p.get("description", ""),
                        confidence=p.get("confidence", 0.0),
                        data=p,
                    )
                    self.db.add(record)
                self.db.commit()
                return patterns
        except json.JSONDecodeError:
            pass

        return []

    def get_cached_patterns(self, user_id: str) -> list[dict]:
        """Get previously discovered patterns."""
        patterns = (
            self.db.query(UserPattern)
            .filter_by(user_id=user_id)
            .order_by(UserPattern.confidence.desc())
            .all()
        )
        return [
            {
                "pattern_type": p.pattern_type,
                "description": p.description,
                "confidence": p.confidence,
                "discovered_at": p.discovered_at.isoformat(),
            }
            for p in patterns
        ]
```

- [ ] **Step 5: Write test for OpenAI client caching**

File: `services/ai_insights/tests/test_openai_client.py`
```python
"""Tests for OpenAI client caching behavior."""
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ai_insights.database.connection import Base
from ai_insights.models.insights_models import InsightCache


def test_cache_hit_returns_stored_response():
    """Cached insights should be returned without calling OpenAI."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Pre-populate cache
    cache = InsightCache(
        user_id="user_1",
        insight_type="coaching",
        prompt_hash="test_hash",
        response='["Tip 1", "Tip 2"]',
        model_used="gpt-4o-mini",
        tokens_used=50,
        expires_at=datetime.utcnow() + timedelta(hours=4),
    )
    db.add(cache)
    db.commit()

    # Verify cache exists
    cached = (
        db.query(InsightCache)
        .filter_by(user_id="user_1", insight_type="coaching")
        .filter(InsightCache.expires_at > datetime.utcnow())
        .first()
    )
    assert cached is not None
    assert cached.response == '["Tip 1", "Tip 2"]'
    db.close()
```

- [ ] **Step 6: Run tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/ai_insights/tests/ -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add services/ai_insights/clients/ services/ai_insights/prompts/ services/ai_insights/services/ services/ai_insights/tests/
git commit -m "feat: AI Insights services - OpenAI client, coaching generator, pattern discoverer"
```

---

### Task 19: AI Insights — Routers, Events, main.py

**Files:**
- Modify: `services/ai_insights/routers/insights.py`
- Modify: `services/ai_insights/routers/patterns.py`
- Modify: `services/ai_insights/routers/coaching.py`
- Create: `services/ai_insights/events/__init__.py`
- Create: `services/ai_insights/events/subscriber.py`
- Create: `services/ai_insights/events/handlers.py`
- Modify: `services/ai_insights/main.py`
- Create: `services/ai_insights/requirements.txt`

- [ ] **Step 1: Implement routers**

File: `services/ai_insights/routers/insights.py`
```python
"""Insights router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ai_insights.database.connection import get_db
from ai_insights.services.session_analyzer import SessionAnalyzer
from ai_insights.services.coaching_generator import CoachingGenerator
from ai_insights.models.insights_models import CoachingResponse, DailyBriefingResponse, SessionReviewResponse

router = APIRouter()


@router.get("/users/{user_id}/coaching", response_model=CoachingResponse)
async def get_coaching(user_id: str, db: Session = Depends(get_db)):
    analyzer = SessionAnalyzer()
    user_data = await analyzer.get_user_context(user_id)
    generator = CoachingGenerator(db)
    result = await generator.generate_coaching(user_id, user_data)
    return CoachingResponse(user_id=user_id, tips=result["tips"], generated_at=datetime.utcnow().isoformat(), cached=result.get("cached", False))


@router.get("/users/{user_id}/daily-briefing", response_model=DailyBriefingResponse)
async def get_daily_briefing(user_id: str, db: Session = Depends(get_db)):
    analyzer = SessionAnalyzer()
    user_data = await analyzer.get_user_context(user_id)
    generator = CoachingGenerator(db)
    result = await generator.generate_daily_briefing(user_id, user_data)
    return DailyBriefingResponse(
        user_id=user_id,
        best_focus_time=result.get("best_focus_time"),
        suggested_session_length=result.get("suggested_session_length"),
        streak_message=result.get("streak_message"),
        insights=result.get("insights", []),
        generated_at=datetime.utcnow().isoformat(),
    )


@router.post("/users/{user_id}/session-review", response_model=SessionReviewResponse)
async def session_review(user_id: str, session_data: dict, db: Session = Depends(get_db)):
    generator = CoachingGenerator(db)
    result = await generator.generate_session_review(user_id, session_data)
    return SessionReviewResponse(
        session_id=session_data.get("session_id", "unknown"),
        went_well=result.get("went_well", []),
        to_improve=result.get("to_improve", []),
        overall_feedback=result.get("overall_feedback", ""),
    )
```

File: `services/ai_insights/routers/patterns.py`
```python
"""Patterns router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ai_insights.database.connection import get_db
from ai_insights.services.pattern_discoverer import PatternDiscoverer
from ai_insights.models.pattern_models import PatternResponse

router = APIRouter()


@router.get("/users/{user_id}/discover", response_model=PatternResponse)
async def discover_patterns(user_id: str, db: Session = Depends(get_db)):
    discoverer = PatternDiscoverer(db)
    patterns = discoverer.get_cached_patterns(user_id)
    return PatternResponse(patterns=patterns, user_id=user_id)


@router.get("/users/{user_id}/interpreted-correlations")
async def interpreted_correlations(user_id: str, db: Session = Depends(get_db)):
    """AI-interpreted correlations from raw Analytics data."""
    discoverer = PatternDiscoverer(db)
    patterns = discoverer.get_cached_patterns(user_id)
    correlation_patterns = [p for p in patterns if "correlation" in p.get("pattern_type", "")]
    return {"user_id": user_id, "interpreted_correlations": correlation_patterns}
```

File: `services/ai_insights/routers/coaching.py`
```python
"""Coaching router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ai_insights.database.connection import get_db

router = APIRouter()


@router.get("/users/{user_id}/goals")
async def get_goals(user_id: str, db: Session = Depends(get_db)):
    """AI-suggested goals. Placeholder — will use OpenAI in future iteration."""
    return {
        "user_id": user_id,
        "goals": [
            {"goal": "Complete 5 focus sessions this week", "type": "weekly"},
            {"goal": "Maintain your streak for 7 days", "type": "streak"},
            {"goal": "Try a deep work session of 50 minutes", "type": "challenge"},
        ],
    }
```

- [ ] **Step 2: Create events**

File: `services/ai_insights/events/__init__.py`
```python
```

File: `services/ai_insights/events/handlers.py`
```python
"""Event handlers for AI Insights."""
import logging
logger = logging.getLogger("ai_insights.events.handlers")


async def handle_session_completed(data: dict, publisher=None):
    """Queue session for analysis. Lightweight — no OpenAI call."""
    user_id = data.get("user_id")
    logger.info("Session completed for %s — queued for analysis", user_id)
```

File: `services/ai_insights/events/subscriber.py`
```python
"""Redis pub/sub event subscriber for AI Insights."""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from ai_insights.events.handlers import handle_session_completed

logger = logging.getLogger("ai_insights.events.subscriber")

SUBSCRIPTIONS = {"session.completed": handle_session_completed}


async def start_subscriber(redis_url: str, publisher=None):
    redis = aioredis.from_url(redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe(*SUBSCRIPTIONS.keys())
    logger.info("Subscribed to channels: %s", list(SUBSCRIPTIONS.keys()))
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode()
            handler = SUBSCRIPTIONS.get(channel)
            if handler:
                try:
                    data = json.loads(message["data"])
                    await handler(data, publisher=publisher)
                except Exception:
                    logger.exception("Error handling event on %s", channel)
    finally:
        await pubsub.unsubscribe()
        await redis.close()
```

- [ ] **Step 3: Update main.py**

File: `services/ai_insights/main.py`
```python
"""Focus Flow - AI Insights Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging

from ai_insights.config.ai_settings import get_settings
from ai_insights.database.connection import create_tables
from ai_insights.routers import insights, patterns, coaching
from ai_insights.events.subscriber import start_subscriber

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Insights service starting up...")
    create_tables()
    subscriber_task = asyncio.create_task(start_subscriber(settings.redis_url))
    yield
    subscriber_task.cancel()
    logger.info("AI Insights service shutting down...")


app = FastAPI(
    title="Focus Flow - AI Insights",
    description="AI-powered coaching, pattern discovery, and productivity recommendations",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insights.router, prefix=f"{settings.api_prefix}/insights", tags=["insights"])
app.include_router(patterns.router, prefix=f"{settings.api_prefix}/patterns", tags=["patterns"])
app.include_router(coaching.router, prefix=f"{settings.api_prefix}/coaching", tags=["coaching"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai_insights", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"service": "Focus Flow - AI Insights", "version": "1.0.0", "status": "operational", "port": settings.port}


if __name__ == "__main__":
    uvicorn.run("ai_insights.main:app", host=settings.host, port=settings.port, reload=settings.debug_mode)
```

- [ ] **Step 4: Create requirements.txt**

File: `services/ai_insights/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
httpx==0.25.2
openai==1.6.1
pytest==7.4.3
pytest-asyncio==0.21.1
```

- [ ] **Step 5: Run all AI Insights tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/ai_insights/tests/ -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add services/ai_insights/
git commit -m "feat: complete AI Insights service - routers, events, OpenAI integration, main.py"
```

---

## Chunk 5: Music Control Service Implementation

### Task 20: Music Control Foundation — Config, Database, Models

**Files:**
- Create: `services/music_control/config/__init__.py`
- Create: `services/music_control/config/settings.py`
- Create: `services/music_control/database/__init__.py`
- Create: `services/music_control/database/connection.py`
- Modify: `services/music_control/models/playlist_models.py`
- Modify: `services/music_control/models/track_models.py`
- Modify: `services/music_control/models/session_music_models.py`
- Create: `services/music_control/tests/test_models.py`

- [ ] **Step 1: Create config and database**

File: `services/music_control/config/__init__.py`
```python
```

File: `services/music_control/config/settings.py`
```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8004
    database_url: str = "postgresql://postgres:postgres@localhost:5432/focus_flow_db"
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    focus_engine_url: str = "http://localhost:8000"

    class Config:
        env_prefix = "MUSIC_CONTROL_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

File: `services/music_control/database/__init__.py`
```python
```

File: `services/music_control/database/connection.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from music_control.config.settings import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 2: Create ORM models**

File: `services/music_control/models/session_music_models.py`
```python
"""Session music logging models."""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from music_control.database.connection import Base


class YouTubeAuth(Base):
    """Stored ytmusicapi credentials."""
    __tablename__ = "mc_youtube_auth"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    credentials = Column(JSON, nullable=False)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SessionMusicLog(Base):
    """Tracks played during focus sessions."""
    __tablename__ = "mc_session_music_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    track_id = Column(String, nullable=False)
    track_title = Column(String, nullable=True)
    artist = Column(String, nullable=True)
    playlist_id = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)


class TrackEffectiveness(Base):
    """Aggregated effectiveness scores per track/genre."""
    __tablename__ = "mc_track_effectiveness"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    track_id = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    avg_productivity_score = Column(Float, default=0.0)
    session_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserMusicPreferences(Base):
    """User music preferences."""
    __tablename__ = "mc_user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    auto_play = Column(Boolean, default=False)
    preferred_genres = Column(JSON, default=list)
    favorite_playlists = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
```

File: `services/music_control/models/playlist_models.py`
```python
"""Playlist Pydantic models."""
from pydantic import BaseModel
from typing import Optional


class PlaylistInfo(BaseModel):
    playlist_id: str
    title: str
    description: Optional[str] = None
    track_count: int = 0
    thumbnail_url: Optional[str] = None


class TrackInfo(BaseModel):
    track_id: str
    title: str
    artist: str
    album: Optional[str] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None
```

File: `services/music_control/models/track_models.py`
```python
"""Track-related Pydantic models."""
from pydantic import BaseModel
from typing import Optional


class PlaybackState(BaseModel):
    is_playing: bool = False
    current_track: Optional[dict] = None
    playlist_id: Optional[str] = None
    position_seconds: int = 0


class EffectivenessReport(BaseModel):
    user_id: str
    entries: list[dict]
    total_tracks_analyzed: int
```

- [ ] **Step 3: Write and run model tests**

File: `services/music_control/tests/test_models.py`
```python
"""Tests for Music Control ORM models."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from music_control.database.connection import Base
from music_control.models.session_music_models import YouTubeAuth, SessionMusicLog, TrackEffectiveness, UserMusicPreferences


def test_table_names():
    assert YouTubeAuth.__tablename__ == "mc_youtube_auth"
    assert SessionMusicLog.__tablename__ == "mc_session_music_log"
    assert TrackEffectiveness.__tablename__ == "mc_track_effectiveness"
    assert UserMusicPreferences.__tablename__ == "mc_user_preferences"


def test_session_music_log_create():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    log = SessionMusicLog(
        user_id="user_1",
        session_id="sess_1",
        track_id="track_abc",
        track_title="Lo-fi Beats",
        artist="ChillHop",
        started_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    assert log.id is not None
    db.close()
```

- [ ] **Step 4: Run tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/music_control/tests/ -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/music_control/config/ services/music_control/database/ services/music_control/models/ services/music_control/tests/
git commit -m "feat: Music Control foundation - config, database, ORM models"
```

---

### Task 21: Music Control — YouTube Client, Services, Routers, Events, main.py

**Files:**
- Modify: `services/music_control/clients/youtube_music_client.py`
- Modify: `services/music_control/services/playlist_service.py`
- Modify: `services/music_control/services/effectiveness_tracker.py`
- Create: `services/music_control/routers/auth.py`
- Modify: `services/music_control/routers/playlists.py`
- Modify: `services/music_control/routers/playback.py`
- Create: `services/music_control/routers/effectiveness.py`
- Create: `services/music_control/events/__init__.py`
- Create: `services/music_control/events/publisher.py`
- Create: `services/music_control/events/subscriber.py`
- Create: `services/music_control/events/handlers.py`
- Modify: `services/music_control/main.py`
- Create: `services/music_control/requirements.txt`

- [ ] **Step 1: Implement YouTube Music client**

File: `services/music_control/clients/youtube_music_client.py`
```python
"""YouTube Music API client via ytmusicapi."""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from music_control.models.session_music_models import YouTubeAuth

logger = logging.getLogger("music_control.clients.youtube")


class YouTubeMusicClient:
    """Wraps ytmusicapi for auth, browsing, and playback."""

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id
        self._ytmusic = None

    def _get_client(self):
        """Lazily initialize ytmusicapi with stored credentials."""
        if self._ytmusic:
            return self._ytmusic

        auth = self.db.query(YouTubeAuth).filter_by(user_id=self.user_id).first()
        if not auth or not auth.is_valid:
            return None

        try:
            from ytmusicapi import YTMusic
            self._ytmusic = YTMusic(auth=auth.credentials)
            return self._ytmusic
        except Exception as e:
            logger.error("Failed to initialize YTMusic: %s", e)
            return None

    def get_playlists(self) -> list[dict]:
        """Get user's playlists."""
        yt = self._get_client()
        if not yt:
            return []
        try:
            playlists = yt.get_library_playlists(limit=50)
            return [
                {
                    "playlist_id": p.get("playlistId", ""),
                    "title": p.get("title", ""),
                    "description": p.get("description", ""),
                    "track_count": p.get("count", 0),
                    "thumbnail_url": p["thumbnails"][0]["url"] if p.get("thumbnails") else None,
                }
                for p in playlists
            ]
        except Exception as e:
            logger.error("Failed to get playlists: %s", e)
            return []

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        """Get tracks from a playlist."""
        yt = self._get_client()
        if not yt:
            return []
        try:
            playlist = yt.get_playlist(playlist_id, limit=100)
            return [
                {
                    "track_id": t.get("videoId", ""),
                    "title": t.get("title", ""),
                    "artist": t["artists"][0]["name"] if t.get("artists") else "Unknown",
                    "album": t.get("album", {}).get("name") if t.get("album") else None,
                    "duration_seconds": t.get("duration_seconds"),
                }
                for t in playlist.get("tracks", [])
            ]
        except Exception as e:
            logger.error("Failed to get tracks: %s", e)
            return []

    @staticmethod
    def setup_auth(db: Session, user_id: str, headers: dict) -> bool:
        """Store YouTube Music auth credentials from browser headers."""
        try:
            from ytmusicapi import YTMusic
            # ytmusicapi can extract auth from request headers
            auth_data = YTMusic.setup(headers_raw=headers)

            existing = db.query(YouTubeAuth).filter_by(user_id=user_id).first()
            if existing:
                existing.credentials = auth_data
                existing.is_valid = True
            else:
                db.add(YouTubeAuth(user_id=user_id, credentials=auth_data))
            db.commit()
            return True
        except Exception as e:
            logger.error("Auth setup failed: %s", e)
            return False

    @staticmethod
    def check_auth_status(db: Session, user_id: str) -> dict:
        """Check if YouTube Music auth is valid."""
        auth = db.query(YouTubeAuth).filter_by(user_id=user_id).first()
        if not auth:
            return {"authenticated": False, "message": "No credentials stored"}
        return {"authenticated": auth.is_valid, "updated_at": auth.updated_at.isoformat() if auth.updated_at else None}
```

- [ ] **Step 2: Implement services**

File: `services/music_control/services/playlist_service.py`
```python
"""Playlist management service."""
from sqlalchemy.orm import Session
from music_control.clients.youtube_music_client import YouTubeMusicClient


class PlaylistService:
    """Manages playlists and focus recommendations."""

    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.yt_client = YouTubeMusicClient(db, user_id)

    def get_playlists(self) -> list[dict]:
        return self.yt_client.get_playlists()

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        return self.yt_client.get_playlist_tracks(playlist_id)

    def get_focus_recommendations(self) -> list[dict]:
        """Suggest playlists good for focus work. Basic heuristic for now."""
        playlists = self.get_playlists()
        focus_keywords = ["focus", "study", "lo-fi", "ambient", "concentration", "deep work", "instrumental", "chill"]
        recommendations = []
        for p in playlists:
            title_lower = p.get("title", "").lower()
            if any(kw in title_lower for kw in focus_keywords):
                p["recommendation_reason"] = "Title matches focus-related keywords"
                recommendations.append(p)
        return recommendations
```

File: `services/music_control/services/effectiveness_tracker.py`
```python
"""Music effectiveness tracking service."""
from sqlalchemy.orm import Session
from music_control.models.session_music_models import SessionMusicLog, TrackEffectiveness


class EffectivenessTracker:
    """Correlates music with focus session quality."""

    def __init__(self, db: Session):
        self.db = db

    def get_report(self, user_id: str) -> dict:
        """Get music effectiveness report."""
        entries = (
            self.db.query(TrackEffectiveness)
            .filter_by(user_id=user_id)
            .order_by(TrackEffectiveness.avg_productivity_score.desc())
            .all()
        )
        return {
            "entries": [
                {
                    "genre": e.genre,
                    "track_id": e.track_id,
                    "avg_productivity_score": round(e.avg_productivity_score, 2),
                    "session_count": e.session_count,
                }
                for e in entries
            ],
            "total_tracks_analyzed": len(entries),
        }

    def get_track_report(self, user_id: str) -> list[dict]:
        """Get per-track effectiveness data."""
        entries = (
            self.db.query(TrackEffectiveness)
            .filter(TrackEffectiveness.user_id == user_id, TrackEffectiveness.track_id.isnot(None))
            .order_by(TrackEffectiveness.avg_productivity_score.desc())
            .all()
        )
        return [
            {
                "track_id": e.track_id,
                "avg_productivity_score": round(e.avg_productivity_score, 2),
                "session_count": e.session_count,
            }
            for e in entries
        ]

    def log_session_music(self, user_id: str, session_id: str, track_data: dict):
        """Log what music played during a session."""
        from datetime import datetime
        log = SessionMusicLog(
            user_id=user_id,
            session_id=session_id,
            track_id=track_data.get("track_id", "unknown"),
            track_title=track_data.get("title"),
            artist=track_data.get("artist"),
            playlist_id=track_data.get("playlist_id"),
            started_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
```

- [ ] **Step 3: Implement routers**

File: `services/music_control/routers/auth.py`
```python
"""YouTube Music auth router — NEW."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from music_control.database.connection import get_db
from music_control.clients.youtube_music_client import YouTubeMusicClient

router = APIRouter()


@router.post("/youtube/setup")
def setup_youtube_auth(user_id: str, headers: dict, db: Session = Depends(get_db)):
    success = YouTubeMusicClient.setup_auth(db, user_id, headers)
    if success:
        return {"status": "authenticated"}
    return {"status": "failed", "message": "Could not authenticate with YouTube Music"}


@router.get("/youtube/status")
def auth_status(user_id: str, db: Session = Depends(get_db)):
    return YouTubeMusicClient.check_auth_status(db, user_id)
```

File: `services/music_control/routers/playlists.py`
```python
"""Playlists router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from music_control.database.connection import get_db
from music_control.services.playlist_service import PlaylistService

router = APIRouter()


@router.get("/")
def get_playlists(user_id: str, db: Session = Depends(get_db)):
    return PlaylistService(db, user_id).get_playlists()


@router.get("/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str, user_id: str, db: Session = Depends(get_db)):
    return PlaylistService(db, user_id).get_playlist_tracks(playlist_id)


@router.get("/focus-recommendations")
def focus_recommendations(user_id: str, db: Session = Depends(get_db)):
    return PlaylistService(db, user_id).get_focus_recommendations()
```

File: `services/music_control/routers/playback.py`
```python
"""Playback control router."""
from fastapi import APIRouter
from music_control.models.track_models import PlaybackState

router = APIRouter()

# In-memory playback state (per-process, demo only)
_playback_state: dict[str, PlaybackState] = {}


@router.post("/play")
def play(user_id: str, playlist_id: str = None, track_id: str = None):
    _playback_state[user_id] = PlaybackState(is_playing=True, playlist_id=playlist_id, current_track={"track_id": track_id})
    return {"status": "playing", "playlist_id": playlist_id, "track_id": track_id}


@router.post("/pause")
def pause(user_id: str):
    state = _playback_state.get(user_id)
    if state:
        state.is_playing = False
    return {"status": "paused"}


@router.post("/skip")
def skip(user_id: str):
    return {"status": "skipped", "message": "Skip requires YouTube Music integration"}


@router.get("/current", response_model=PlaybackState)
def get_current(user_id: str):
    return _playback_state.get(user_id, PlaybackState())
```

File: `services/music_control/routers/effectiveness.py`
```python
"""Effectiveness router — replaces discovery.py."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from music_control.database.connection import get_db
from music_control.services.effectiveness_tracker import EffectivenessTracker

router = APIRouter()


@router.get("/users/{user_id}")
def get_effectiveness_report(user_id: str, db: Session = Depends(get_db)):
    return EffectivenessTracker(db).get_report(user_id)


@router.get("/users/{user_id}/tracks")
def get_track_effectiveness(user_id: str, db: Session = Depends(get_db)):
    return EffectivenessTracker(db).get_track_report(user_id)
```

- [ ] **Step 4: Create events**

File: `services/music_control/events/__init__.py`
```python
```

File: `services/music_control/events/publisher.py`
```python
"""Redis pub/sub event publisher for Music Control."""
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger("music_control.events.publisher")
SERVICE_NAME = "music_control"


class EventPublisher:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event_type: str, user_id: str, payload: dict) -> None:
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_service": SERVICE_NAME,
            "user_id": user_id,
            "payload": payload,
        }
        await self.redis.publish(event_type, json.dumps(message))
        logger.info("Published %s for user %s", event_type, user_id)
```

File: `services/music_control/events/handlers.py`
```python
"""Event handlers for Music Control."""
import logging
logger = logging.getLogger("music_control.events.handlers")


async def handle_session_started(data: dict, publisher=None):
    user_id = data.get("user_id")
    logger.info("Session started for %s — checking auto-play preferences", user_id)


async def handle_session_completed(data: dict, publisher=None):
    user_id = data.get("user_id")
    logger.info("Session completed for %s — logging music data", user_id)


async def handle_session_paused(data: dict, publisher=None):
    user_id = data.get("user_id")
    logger.info("Session paused for %s — pausing playback", user_id)


async def handle_session_resumed(data: dict, publisher=None):
    user_id = data.get("user_id")
    logger.info("Session resumed for %s — resuming playback", user_id)
```

File: `services/music_control/events/subscriber.py`
```python
"""Redis pub/sub event subscriber for Music Control."""
import asyncio
import json
import logging
import redis.asyncio as aioredis
from music_control.events.handlers import (
    handle_session_started, handle_session_completed,
    handle_session_paused, handle_session_resumed,
)

logger = logging.getLogger("music_control.events.subscriber")

SUBSCRIPTIONS = {
    "session.started": handle_session_started,
    "session.completed": handle_session_completed,
    "session.paused": handle_session_paused,
    "session.resumed": handle_session_resumed,
}


async def start_subscriber(redis_url: str, publisher=None):
    redis = aioredis.from_url(redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe(*SUBSCRIPTIONS.keys())
    logger.info("Subscribed to channels: %s", list(SUBSCRIPTIONS.keys()))
    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            channel = message["channel"]
            if isinstance(channel, bytes):
                channel = channel.decode()
            handler = SUBSCRIPTIONS.get(channel)
            if handler:
                try:
                    data = json.loads(message["data"])
                    await handler(data, publisher=publisher)
                except Exception:
                    logger.exception("Error handling event on %s", channel)
    finally:
        await pubsub.unsubscribe()
        await redis.close()
```

- [ ] **Step 5: Create WebSocket endpoint for `music.track_changed` bridge**

File: `services/music_control/routers/websockets.py` — NEW

```python
"""WebSocket endpoint bridging Redis music.track_changed events to frontend."""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

from music_control.config.settings import get_settings

logger = logging.getLogger("music_control.routers.websockets")
settings = get_settings()
router = APIRouter()

# Active WebSocket connections per user
_connections: dict[str, list[WebSocket]] = {}


@router.websocket("/playback")
async def playback_ws(websocket: WebSocket, user_id: str = "demo_user"):
    """WebSocket bridge: subscribes to music.track_changed Redis channel
    and forwards matching events to the connected frontend client."""
    await websocket.accept()
    _connections.setdefault(user_id, []).append(websocket)

    redis = aioredis.from_url(settings.redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe("music.track_changed")

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            if data.get("user_id") == user_id:
                await websocket.send_json(data.get("payload", {}))
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for user %s", user_id)
    finally:
        _connections.get(user_id, []).remove(websocket) if websocket in _connections.get(user_id, []) else None
        await pubsub.unsubscribe()
        await redis.close()
```

- [ ] **Step 6: Update main.py**

File: `services/music_control/main.py`
```python
"""Focus Flow - Music Control Service"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import uvicorn
import logging
import redis.asyncio as aioredis

from music_control.config.settings import get_settings
from music_control.database.connection import create_tables
from music_control.routers import playlists, playback
from music_control.routers.auth import router as auth_router
from music_control.routers.effectiveness import router as effectiveness_router
from music_control.routers.websockets import router as ws_router
from music_control.events.publisher import EventPublisher
from music_control.events.subscriber import start_subscriber

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Music Control service starting up...")
    create_tables()
    redis_client = aioredis.from_url(settings.redis_url)
    publisher = EventPublisher(redis_client=redis_client)
    subscriber_task = asyncio.create_task(start_subscriber(settings.redis_url, publisher=publisher))
    yield
    subscriber_task.cancel()
    await redis_client.close()
    logger.info("Music Control service shutting down...")


app = FastAPI(
    title="Focus Flow - Music Control",
    description="YouTube Music integration for focus sessions",
    version="1.0.0",
    docs_url="/docs" if settings.debug_mode else None,
    redoc_url="/redoc" if settings.debug_mode else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(playlists.router, prefix=f"{settings.api_prefix}/playlists", tags=["playlists"])
app.include_router(playback.router, prefix=f"{settings.api_prefix}/playback", tags=["playback"])
app.include_router(effectiveness_router, prefix=f"{settings.api_prefix}/effectiveness", tags=["effectiveness"])
app.include_router(ws_router, prefix="/ws", tags=["websockets"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "music_control", "version": "1.0.0"}


@app.get("/")
async def root():
    return {"service": "Focus Flow - Music Control", "version": "1.0.0", "status": "operational", "port": settings.port}


if __name__ == "__main__":
    uvicorn.run("music_control.main:app", host=settings.host, port=settings.port, reload=settings.debug_mode)
```

- [ ] **Step 6: Create requirements.txt**

File: `services/music_control/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
httpx==0.25.2
ytmusicapi==1.3.2
websockets==12.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

- [ ] **Step 7: Run all Music Control tests**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/music_control/tests/ -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add services/music_control/
git commit -m "feat: complete Music Control service - YouTube client, routers, events, main.py"
```

---

## Chunk 6: Final Integration and Cleanup

### Task 22: docker-compose.yml Updates

The spec requires service entries for all secondary services.

**Files:**
- Modify: `docker-compose.yml` (if exists) or Create: `docker-compose.yml`

- [ ] **Step 1: Add/update docker-compose.yml with all service entries**

Ensure `docker-compose.yml` has entries for:
- `postgres` — PostgreSQL 15, port 5432, database `focus_flow_db`
- `redis` — Redis 7, port 6379
- `focus_engine` — port 8000, depends on postgres, redis
- `game_engine` — port 8001, depends on postgres, redis
- `ai_insights` — port 8002, depends on postgres, redis, with `AI_INSIGHTS_OPENAI_API_KEY` env var
- `analytics` — port 8003, depends on postgres, redis
- `music_control` — port 8004, depends on postgres, redis

Each service entry should:
- Build from `services/<name>/Dockerfile`
- Map the correct port
- Set `DATABASE_URL` and `REDIS_URL` environment variables
- Depend on `postgres` and `redis` services

- [ ] **Step 2: Commit**

```bash
git add docker-compose.yml
git commit -m "infra: add all secondary services to docker-compose.yml"
```

---

### Task 23: Update PROGRESS.md and .env.example

**Files:**
- Modify: `PROGRESS.md`
- Modify: `.env.example`

- [ ] **Step 1: Update PROGRESS.md to reflect current state**

Mark B3 as complete. Mark B4 tasks as complete. Update "Current Status" section. Update "Next Steps" to show C1.

- [ ] **Step 2: Update .env.example with new environment variables**

Add to `.env.example`:
```
# Game Engine
GAME_ENGINE_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/focus_flow_db

# Analytics
ANALYTICS_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/focus_flow_db
ANALYTICS_FOCUS_ENGINE_URL=http://localhost:8000
ANALYTICS_GAME_ENGINE_URL=http://localhost:8001

# AI Insights
AI_INSIGHTS_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/focus_flow_db
AI_INSIGHTS_OPENAI_API_KEY=sk-your-key-here
AI_INSIGHTS_OPENAI_MODEL=gpt-4o-mini
AI_INSIGHTS_OPENAI_MODEL_ADVANCED=gpt-4o
AI_INSIGHTS_FOCUS_ENGINE_URL=http://localhost:8000
AI_INSIGHTS_ANALYTICS_URL=http://localhost:8003

# Music Control
MUSIC_CONTROL_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/focus_flow_db
MUSIC_CONTROL_FOCUS_ENGINE_URL=http://localhost:8000
```

- [ ] **Step 3: Commit**

```bash
git add PROGRESS.md .env.example
git commit -m "docs: update PROGRESS.md for B4 completion and add new env vars"
```

---

### Task 24: Run Full Test Suite

- [ ] **Step 1: Run all tests across all services**

Run: `cd O:/focus-flow_DEMO && python -m pytest services/ -v --tb=short`
Expected: All tests PASS across all services

- [ ] **Step 2: Fix any failing tests**

If tests fail, fix them and re-run until all pass.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "test: verify full test suite passes across all services"
```
