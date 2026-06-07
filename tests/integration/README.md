# E2E Event Chain Integration Test

Proves the cross-service Redis event chain works end-to-end against the live docker-compose stack. Per-service unit tests use mocked Redis, so this is the only thing that catches breakage in the actual pub/sub path.

## What it asserts

A single `session.completed` event published by `focus_engine` produces:

| Service | DB write |
|---|---|
| `game_engine` | `ge_xp_history` row, `ge_user_streaks` (current_streak >= 1), `ge_user_levels` row |
| `analytics` | `an_daily_aggregates` row for today (total_sessions >= 1) |

## What it does NOT assert (yet)

| Service | Reason |
|---|---|
| `ai_insights` | Handler is log-only. LLM calls happen on-demand via REST endpoints (`/insights`, `/patterns`, `/coaching`), not on event receipt. |
| `music_control` | All four handlers (`session.started/completed/paused/resumed`) are placeholder log-only stubs. No DB writes implemented yet. |

When either of those handlers grow real behavior, add the assertion to `test_event_chain.py`.

## Precondition

The full docker-compose stack must be up and all 5 services + Postgres + Redis healthy.

```bash
# From repo root
docker-compose up -d --build
docker-compose ps        # all should be "healthy" or "running"
```

Healthchecks take ~20-30 seconds on first boot. Subsequent boots are faster.

## Run

```bash
# From repo root
make integration-test
```

Or manually:

```bash
python -m venv tests/integration/.venv
source tests/integration/.venv/bin/activate
pip install -r tests/integration/requirements.txt
pytest tests/integration/ -o testpaths=tests/integration -o pythonpath= -v
```

The `-o` overrides are required because the repo-root `pytest.ini` scopes pytest to the per-service unit tests under `services/`.

## Environment overrides

| Env var | Default | Purpose |
|---|---|---|
| `FOCUS_ENGINE_URL` | `http://localhost:8000` | Where to POST session lifecycle calls |
| `POSTGRES_DSN` | `postgresql://postgres:postgres@localhost:5432/focus_flow_db` | Where to assert DB writes |

Use these to point the test at a remote stack (e.g., a Railway preview deploy) once hosting is set up.

## Cleanup

Test rows are scoped by a per-run `user_id` of the form `e2e_<uuid8>`. To purge them between runs:

```bash
docker-compose exec postgres psql -U postgres -d focus_flow_db -c "
DELETE FROM ge_xp_history       WHERE user_id LIKE 'e2e_%';
DELETE FROM ge_user_streaks     WHERE user_id LIKE 'e2e_%';
DELETE FROM ge_user_levels      WHERE user_id LIKE 'e2e_%';
DELETE FROM ge_user_achievements WHERE user_id LIKE 'e2e_%';
DELETE FROM an_daily_aggregates WHERE user_id LIKE 'e2e_%';
DELETE FROM fe_focus_sessions   WHERE user_id LIKE 'e2e_%';
"
```

Not strictly necessary — the unique `user_id` prevents cross-run interference — but useful before a clean demo.

## Troubleshooting

- **Test fails on `focus_engine root` assertion:** stack isn't up. Run `docker-compose up -d` and wait for healthchecks.
- **Test fails on `ge_xp_history` timeout but `focus_engine` succeeded:** `game_engine` subscriber didn't process. Check `docker-compose logs game_engine` for the handler error.
- **Test fails on `an_daily_aggregates` timeout but game_engine assertions passed:** `analytics` subscriber didn't process. Check `docker-compose logs analytics`.
- **All assertions time out:** likely Redis pub/sub isn't reaching subscribers. Check `docker-compose logs redis` and verify each service logs "Started Redis subscriber" or similar at startup.
