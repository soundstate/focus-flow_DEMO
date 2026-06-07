"""Shared fixtures for the e2e event-chain integration test.

The fixtures assume the full docker-compose stack is already running
locally on the default ports (postgres 5432, focus_engine 8000, etc.).
See tests/integration/README.md for the run recipe.
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Callable

import httpx
import psycopg
import pytest


FOCUS_ENGINE_URL = os.environ.get("FOCUS_ENGINE_URL", "http://localhost:8000")
POSTGRES_DSN = os.environ.get(
    "POSTGRES_DSN",
    "postgresql://postgres:postgres@localhost:5432/focus_flow_db",
)


def wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = 15.0,
    interval: float = 0.25,
) -> bool:
    """Poll predicate until it returns True or timeout elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


@pytest.fixture(scope="session")
def pg_conn():
    conn = psycopg.connect(POSTGRES_DSN, autocommit=True)
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def http():
    with httpx.Client(base_url=FOCUS_ENGINE_URL, timeout=10.0) as client:
        yield client


@pytest.fixture
def user_id() -> str:
    """Unique per-test user_id so runs don't collide. Prefix `e2e_` lets
    you bulk-delete test rows: `DELETE ... WHERE user_id LIKE 'e2e_%'`."""
    return f"e2e_{uuid.uuid4().hex[:12]}"
