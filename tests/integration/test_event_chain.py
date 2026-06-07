"""End-to-end event chain integration test.

Proves that a session.completed event published by focus_engine
propagates through Redis to the game_engine and analytics subscribers
and produces the expected DB writes within a bounded time window.

Scope and known limitations (as of 2026-05-26):
  - game_engine subscriber: ASSERTED. Writes ge_xp_history,
    ge_user_streaks, ge_user_levels rows.
  - analytics subscriber:   ASSERTED. Writes an_daily_aggregates row.
  - ai_insights subscriber: NOT ASSERTED. Handler is log-only;
    LLM calls happen on-demand via REST endpoints, not on event
    receipt. When event-driven coaching artifacts land, add an
    assertion here.
  - music_control subscriber: NOT ASSERTED. Handlers are placeholder
    log-only stubs (no DB writes implemented yet). When session-music
    linking lands, add an assertion here.

Precondition: docker-compose stack must be up and all services healthy.
See tests/integration/README.md.
"""

from __future__ import annotations

from .conftest import wait_until


def test_session_completion_propagates_to_subscribers(http, pg_conn, user_id):
    # Sanity: focus_engine is reachable
    root = http.get("/")
    assert root.status_code == 200, f"focus_engine root: {root.status_code} {root.text}"

    # 1. Create session via focus_engine API
    create = http.post(
        "/api/v1/sessions/",
        json={
            "user_id": user_id,
            "session_type": "pomodoro",
            "planned_duration": 25,
        },
    )
    assert create.status_code == 201, f"create session: {create.status_code} {create.text}"
    session_id = create.json()["id"]

    # 2. Complete session — this triggers EventPublisher.publish('session.completed', ...)
    complete = http.post(
        f"/api/v1/sessions/{session_id}/complete",
        params={"completion_reason": "test"},
    )
    assert complete.status_code == 200, f"complete session: {complete.status_code} {complete.text}"

    # 3. game_engine subscriber → ge_xp_history row appears
    def xp_history_row_exists() -> bool:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM ge_xp_history WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone()[0] >= 1

    assert wait_until(xp_history_row_exists), (
        f"timeout waiting for ge_xp_history row for user_id={user_id} -- "
        f"game_engine subscriber did not process session.completed"
    )

    # 4. game_engine subscriber → ge_user_streaks row with current_streak >= 1
    def streak_started() -> bool:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT current_streak FROM ge_user_streaks WHERE user_id = %s",
                (user_id,),
            )
            row = cur.fetchone()
            return row is not None and row[0] >= 1

    assert wait_until(streak_started), (
        f"timeout waiting for ge_user_streaks (current_streak>=1) for user_id={user_id}"
    )

    # 5. game_engine subscriber → ge_user_levels row exists (XP awarded)
    def level_row_exists() -> bool:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM ge_user_levels WHERE user_id = %s",
                (user_id,),
            )
            return cur.fetchone()[0] >= 1

    assert wait_until(level_row_exists), (
        f"timeout waiting for ge_user_levels row for user_id={user_id}"
    )

    # 6. analytics subscriber → an_daily_aggregates row for today, total_sessions >= 1
    def aggregate_row_exists() -> bool:
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT total_sessions FROM an_daily_aggregates "
                "WHERE user_id = %s AND date = CURRENT_DATE",
                (user_id,),
            )
            row = cur.fetchone()
            return row is not None and row[0] >= 1

    assert wait_until(aggregate_row_exists), (
        f"timeout waiting for an_daily_aggregates row for user_id={user_id} on today's date "
        f"-- analytics subscriber did not process session.completed"
    )
