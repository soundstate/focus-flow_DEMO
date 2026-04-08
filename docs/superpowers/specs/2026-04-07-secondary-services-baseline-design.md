# Secondary Services Baseline — Design Spec

**Date:** 2026-04-07
**Phase:** B4 — Secondary Services Integration
**Goal:** Bring all four secondary services (Game Engine, Analytics, AI Insights, Music Control) to a functional baseline with real working endpoints, database persistence, and inter-service communication.

---

## 1. Architecture & Service Communication

### Event Bus (Redis Pub/Sub)
- Focus Engine publishes `session.completed`, `session.started`, `session.paused`, `session.resumed` events to Redis
- Game Engine subscribes to `session.completed` — awards XP, checks achievements, updates streaks
- Analytics subscribes to `session.completed`, `achievement.unlocked`, `level.up` — triggers aggregation updates and incorporates gamification milestones
- AI Insights subscribes to `session.completed` — queues pattern analysis
- Music Control subscribes to `session.started`, `session.completed`, `session.paused`, `session.resumed` — manages auto-play, pause/resume, and logging

### Synchronous HTTP (for queries)
- Analytics calls Focus Engine (`GET /api/v1/sessions/sessions/user/{user_id}`) to pull session history for aggregation. **Note:** The Focus Engine has a double-prefix bug — the sessions router is mounted at `/api/v1/sessions` and routes inside use `/sessions/...`, resulting in `/api/v1/sessions/sessions/...`. This should be fixed as part of B4 by changing the router's internal paths to not repeat the prefix (e.g., `/sessions/user/{user_id}` → `/user/{user_id}`). After the fix, the corrected path will be `GET /api/v1/sessions/user/{user_id}`.
- Analytics calls Game Engine to pull XP/streak data for cross-service dashboards
- AI Insights calls Focus Engine + Analytics for data to feed into OpenAI prompts
- Frontend calls each service directly (no API gateway for the demo)

### Database Strategy
All services share a single PostgreSQL instance using the default `public` schema with table-name prefixes to avoid collisions. This is simpler and lower-risk than per-service schemas for a demo:
- Focus Engine: `fe_` prefix (existing tables renamed, e.g., `fe_focus_sessions`)
- Game Engine: `ge_` prefix (e.g., `ge_achievements`)
- Analytics: `an_` prefix (e.g., `an_daily_aggregates`)
- AI Insights: `ai_` prefix (e.g., `ai_insight_cache`)
- Music Control: `mc_` prefix (e.g., `mc_session_music_log`)

No `__table_args__` schema changes needed — just set `__tablename__` with the prefix on each model.

### Shared Infrastructure
- Single PostgreSQL instance, shared `public` schema with table-name prefixes
- Redis for both pub/sub events and caching (leaderboards, computed metrics)
- Each service gets an `events/` module with publisher/subscriber logic using a shared pattern

### Service Ports
| Service | Port |
|---|---|
| Focus Engine | 8000 |
| Game Engine | 8001 |
| AI Insights | 8002 |
| Analytics | 8003 |
| Music Control | 8004 |

### Cross-Cutting Concerns
- **Health checks:** All services include `GET /health` and `GET /health/detailed` endpoints following the Focus Engine pattern
- **CORS:** All services allow origins `http://localhost:3000`, `http://localhost:5173` (Vite dev server)
- **Logging:** All services use structured JSON logging via `logging_config.py` following the Focus Engine pattern
- **SQLAlchemy:** New services use `from sqlalchemy.orm import DeclarativeBase` (not the deprecated `declarative_base()` from `ext.declarative`). The existing Game Engine `database/connection.py` uses the deprecated import — migrate it to the new pattern as part of B4 work since models are being reworked anyway.
- **CORS fix:** Focus Engine currently allows `localhost:3000` and `localhost:3001` but not `localhost:5173`. Add `http://localhost:5173` to Focus Engine CORS origins as part of B4 updates.

---

## 2. Game Engine (Port 8001)

### Current State
Models, calculators, and achievement modules exist. Gaps: routers not wired into `main.py`, no service layer connecting calculators to endpoints, no database repository layer, no event subscriber.

### Endpoints (under `/api/v1/`)

**Router: `achievements.py` (prefix: `/achievements`)**
- `GET /achievements/users/{user_id}` — all achievements with unlock status and progress
- `GET /achievements/users/{user_id}/recent` — recently unlocked achievements

**Router: `levels.py` (prefix: `/levels`)**
- `GET /levels/users/{user_id}` — current level, XP, progress to next level
- `GET /levels/users/{user_id}/history` — XP gain history
- `POST /levels/process-session` — manual trigger to process a session (for testing; normally triggered by event)

**Router: `streaks.py` (prefix: `/streaks`)**
- `GET /streaks/users/{user_id}` — current streak, longest streak, milestones

**Router: `leaderboards.py` (prefix: `/leaderboards`)**
- `GET /leaderboards/` — global leaderboard (XP-based, cached in Redis)
- `GET /leaderboards/streaks` — streak leaderboard

### Services
- `AchievementService` — evaluate unlock criteria, track progress, return stats
- `LevelService` — manage XP gains, calculate level-ups, track history
- `StreakService` — update streaks on session complete, handle grace period (36-hour window), detect milestones
- `LeaderboardService` — build/cache leaderboards from Redis sorted sets

### Event Integration
- Subscribes to `session.completed`
- Calls `StreakService.update()`, `LevelService.award_xp()`, `AchievementService.evaluate()` in sequence
- Publishes `achievement.unlocked` and `level.up` events

### Database Tables (prefix `ge_`)
- `ge_user_achievements` — per-user achievement unlock state and progress. Achievement definitions (type, title, description, icon, progress_required) are stored per-row alongside user state (unlocked_at, progress_current, is_unlocked). This denormalizes definitions but keeps the model simple for the demo — one table, one query for a user's full achievement view.
- `ge_user_levels` — XP and level tracking per user
- `ge_user_streaks` — streak state per user
- `ge_xp_history` — log of XP gains with source/reason. **New SQLAlchemy ORM model required** with fields: `id`, `user_id`, `session_id`, `base_xp`, `bonus_xp`, `total_xp`, `reason` (str), `created_at`. The existing `ExperienceGain` Pydantic model is used as the response schema; its `multipliers_applied: dict` field is computed at response time from the calculator, not stored in the ORM model.

---

## 3. Analytics Service (Port 8003)

### Purpose
Cross-service aggregation + advanced time-series analysis beyond Focus Engine's built-in analytics.

### Endpoints (under `/api/v1/`)

**Router: `metrics.py` (prefix: `/metrics`)**
- `GET /metrics/users/{user_id}/dashboard` — unified dashboard metrics from all services (sessions, XP, streaks, productivity scores)
- `GET /metrics/users/{user_id}/summary` — period summary (daily/weekly/monthly totals)

**Router: `trends.py` (prefix: `/trends`)**
- `GET /trends/users/{user_id}/weekly` — week-over-week comparison
- `GET /trends/users/{user_id}/monthly` — month-over-month comparison
- `GET /trends/users/{user_id}/productivity-curve` — time-of-day productivity pattern across all data

**Router: `comparisons.py` (prefix: `/comparisons`)**
- `GET /comparisons/users/{user_id}/periods` — compare two arbitrary date ranges

**Router: `correlations.py` (prefix: `/correlations`) — NEW, not in existing stubs**
- `GET /correlations/users/{user_id}` — cross-service statistical correlations (e.g., streaks vs productivity scores, music genre vs session length)

**Router: `export.py` (prefix: `/export`)**
- `GET /export/users/{user_id}` — CSV/JSON data export of all aggregated metrics

### Services
- `MetricsCalculator` — pulls from Focus Engine + Game Engine via HTTP, computes unified metrics
- `TrendAnalyzer` — statistical trend analysis, moving averages, period comparisons
- `CorrelationProcessor` — finds relationships across session, gamification, and music data
- `ExportService` — formats aggregated data for download

### Event Integration
- Subscribes to `session.completed` — updates pre-computed aggregates and caches
- Subscribes to `achievement.unlocked`, `level.up` — incorporates gamification milestones into trend data

### Database Tables (prefix `an_`)
- `an_daily_aggregates` — pre-computed daily rollups per user (total sessions, total focus time, avg score, XP earned)
- `an_weekly_aggregates` — weekly rollups
- `an_correlation_cache` — stored correlation results (recomputed periodically)

### Design Note
Heavy queries are pre-computed on event receipt and cached. API endpoints serve from aggregates/cache, not raw data.

---

## 4. AI Insights Service (Port 8002)

### Purpose
OpenAI-powered coaching, pattern discovery, and productivity recommendations based on session data.

### Endpoints (under `/api/v1/`)

**Router: `insights.py` (prefix: `/insights`)**
- `GET /insights/users/{user_id}/coaching` — personalized coaching tips based on recent session patterns
- `GET /insights/users/{user_id}/daily-briefing` — daily productivity briefing (best time to focus, suggested session length, streak motivation)
- `POST /insights/users/{user_id}/session-review` — post-session analysis with specific feedback

**Router: `patterns.py` (prefix: `/patterns`)**
- `GET /patterns/users/{user_id}/discover` — discover recurring patterns (e.g., "most productive on Tuesdays")
- `GET /patterns/users/{user_id}/interpreted-correlations` — AI-interpreted correlations (human-readable insights generated from raw Analytics correlation data)

**Router: `coaching.py` (prefix: `/coaching`)**
- `GET /coaching/users/{user_id}/goals` — AI-suggested goals based on performance trajectory

### Services
- `SessionAnalyzer` — gathers session data from Focus Engine, structures it for LLM prompts
- `PatternDiscoverer` — analyzes historical data to find trends, feeds findings to OpenAI for interpretation
- `CoachingGenerator` — builds prompts with user context, calls OpenAI, parses structured responses
- `OpenAIClient` — thin wrapper around OpenAI API with retry logic, token tracking, and response caching

### Prompt Templates (`prompts/` directory)
- `coaching_prompt.txt` — system prompt for coaching persona
- `session_review_prompt.txt` — post-session analysis template
- `pattern_discovery_prompt.txt` — pattern interpretation template
- `daily_briefing_prompt.txt` — briefing generation template

### Cost Management
- Cache OpenAI responses in Redis with TTL (coaching: 4 hours, daily briefing: 12 hours)
- Use `gpt-4o-mini` for routine coaching, `gpt-4o` for deep pattern analysis
- Track token usage per user in database

### Event Integration
- Subscribes to `session.completed` — queues lightweight session review (async, non-blocking)
- Does NOT call OpenAI on every event — batches analysis, generates insights on-demand or on schedule

### Database Tables (prefix `ai_`)
- `ai_insight_cache` — cached LLM responses with TTL and prompt hash
- `ai_user_patterns` — discovered patterns with confidence scores
- `ai_token_usage` — OpenAI token consumption tracking per user

---

## 5. Music Control Service (Port 8004)

### Purpose
YouTube Music integration for focus-session-aware playlist management and music effectiveness tracking.

### Endpoints (under `/api/v1/`)

**Router: `auth.py` (prefix: `/auth`) — NEW, not in existing stubs**
- `POST /auth/youtube/setup` — initialize ytmusicapi authentication (takes browser cookie headers, stores credentials)
- `GET /auth/youtube/status` — check if YouTube Music auth is valid

**Router: `playlists.py` (prefix: `/playlists`)**
- `GET /playlists/` — list user's YouTube Music playlists
- `GET /playlists/{playlist_id}/tracks` — get tracks from a playlist
- `GET /playlists/focus-recommendations` — suggest playlists suited for focus work (genre/tempo analysis)

**Router: `playback.py` (prefix: `/playback`)**
- `POST /playback/play` — start playback (playlist or track)
- `POST /playback/pause` — pause playback
- `POST /playback/skip` — skip current track
- `GET /playback/current` — get currently playing track info

**Router: `effectiveness.py` (prefix: `/effectiveness`) — replaces existing `discovery.py` stub**
- `GET /effectiveness/users/{user_id}` — music effectiveness report (genres/playlists vs productivity scores)
- `GET /effectiveness/users/{user_id}/tracks` — per-track effectiveness data

### Services
- `YouTubeMusicClient` — wraps `ytmusicapi` for auth, playlist browsing, and playback control
- `PlaylistService` — playlist CRUD, focus playlist curation, genre filtering
- `PlaybackService` — manages playback state, tracks what's playing during which session
- `EffectivenessTracker` — correlates music played during sessions with productivity scores from Focus Engine
- `GenreClassifier` — categorizes tracks/playlists by genre for recommendation logic

### Event Integration
- Subscribes to `session.started` — auto-start focus playlist if configured
- Subscribes to `session.completed` — logs what music was playing, feeds into effectiveness tracking
- Subscribes to `session.paused` — pause playback
- Subscribes to `session.resumed` — resume playback
- Publishes `music.track_changed` — bridged to frontend via a WebSocket endpoint at `WS /ws/playback` on this service

### Database Tables (prefix `mc_`)
- `mc_youtube_auth` — stored ytmusicapi credentials per user
- `mc_session_music_log` — which tracks played during which session (session_id, track_id, started_at, ended_at)
- `mc_track_effectiveness` — aggregated effectiveness scores per track/genre
- `mc_user_preferences` — auto-play settings, preferred genres, favorite playlists

### Note
ytmusicapi requires one-time setup with browser request headers from an authenticated YouTube Music session. The `/auth/youtube/setup` endpoint handles this.

---

## 6. Event Bus Infrastructure

### Event Format (JSON over Redis pub/sub)
```json
{
  "event_type": "session.completed",
  "timestamp": "2026-04-07T14:30:00Z",
  "source_service": "focus_engine",
  "user_id": "uuid",
  "payload": {}
}
```

### Event Catalog

| Event | Publisher | Subscribers | Payload Fields |
|---|---|---|---|
| `session.started` | Focus Engine | Music Control | `session_id`, `user_id`, `session_type`, `planned_duration` |
| `session.completed` | Focus Engine | Game Engine, Analytics, AI Insights, Music Control | `session_id`, `user_id`, `session_type`, `actual_duration` (minutes, int), `productivity_score` (float 0.0-10.0), `completed_at`, `interruption_count` (int) |
| `session.paused` | Focus Engine | Music Control | `session_id`, `user_id`, `paused_at` |
| `session.resumed` | Focus Engine | Music Control | `session_id`, `user_id`, `resumed_at` |
| `achievement.unlocked` | Game Engine | Analytics | `user_id`, `achievement_type`, `achievement_title`, `unlocked_at` |
| `level.up` | Game Engine | Analytics | `user_id`, `new_level`, `total_xp`, `leveled_up_at` |
| `music.track_changed` | Music Control | (frontend via Music Control WebSocket) | `user_id`, `track_id`, `track_title`, `artist`, `playlist_id` |

### Implementation Per Service
- `events/publisher.py` — `publish_event(event_type, payload)` using Redis `PUBLISH`
- `events/subscriber.py` — background task that `SUBSCRIBE`s to relevant channels, dispatches to handler functions
- `events/handlers.py` — service-specific handler functions mapped to event types
- Subscriber runs as an asyncio background task started during FastAPI lifespan

### Failure Handling
Events are fire-and-forget for the demo. If a subscriber is down, events are missed. No dead letter queue.

---

## 7. Implementation Order

1. **Event bus infrastructure + Focus Engine updates** — add `events/` module to Focus Engine, publish events on session state changes
2. **Game Engine** — furthest along, no external dependencies
3. **Analytics** — depends on session data from Focus Engine, benefits from Game Engine data
4. **AI Insights** — depends on session + analytics data, requires OpenAI API key
5. **Music Control** — most independent, YouTube Music auth is self-contained

Each service follows the same implementation sequence: database tables/repos → models → services → routers → event integration → wire into main.py.

---

## 8. Modifications to Focus Engine

The Focus Engine needs to be updated to:
- Add `events/publisher.py` module using Redis pub/sub
- Update session service to call publisher after state transitions (`start` → `session.started`, `complete` → `session.completed`, `pause` → `session.paused`, `resume` → `session.resumed`)
- Add `redis` to requirements if not already present
- Rename existing table `focus_sessions` to `fe_focus_sessions` (and `users` to `fe_users`) to follow the prefix convention. Since this is a demo with no production data, drop and recreate tables rather than using Alembic migrations.
- Fix the double-prefix bug in `routers/sessions.py`: change route paths from `/sessions/...` to `/...` since the router is already mounted at `/api/v1/sessions`
- Add `http://localhost:5173` to `cors_origins` default in `config/settings.py`

No other changes to Focus Engine endpoint logic.

---

## 9. Infrastructure Updates

### docker-compose.yml
- Redis already present — no changes needed
- Add service entries for game_engine, analytics, ai_insights, music_control if not present
- Add `OPENAI_API_KEY` to ai_insights service environment

### Environment Variables

**Existing (Focus Engine):**
- `FOCUS_FLOW_DATABASE_URL` — PostgreSQL connection (prefix is `FOCUS_FLOW_`, not `FOCUS_ENGINE_`)
- `FOCUS_FLOW_REDIS_URL` — shared Redis URL

**New:**
- `GAME_ENGINE_DATABASE_URL` — PostgreSQL connection (default should point to shared `focus_flow_db`, not separate `focus_flow_game` database; update Game Engine `settings.py` default accordingly)
- `ANALYTICS_DATABASE_URL` — PostgreSQL connection (shared `focus_flow_db`)
- `AI_INSIGHTS_DATABASE_URL` — PostgreSQL connection (shared `focus_flow_db`)
- `AI_INSIGHTS_OPENAI_API_KEY` — OpenAI API key
- `AI_INSIGHTS_OPENAI_MODEL` — default model (gpt-4o-mini)
- `AI_INSIGHTS_OPENAI_MODEL_ADVANCED` — advanced model (gpt-4o)
- `MUSIC_CONTROL_DATABASE_URL` — PostgreSQL connection for music_control

All services share the same Redis instance and **must use the same Redis database index** (db 0) for pub/sub to work — `SUBSCRIBE` only receives messages published on the same database. Update Game Engine's default `redis_url` from `redis://localhost:6379/1` to `redis://localhost:6379/0` to match Focus Engine. Services can use separate Redis databases for caching if needed, but the event bus publisher/subscriber must share db 0.
