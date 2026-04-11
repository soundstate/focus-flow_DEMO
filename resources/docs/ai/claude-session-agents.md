# Claude Session Agents — Focus Flow

Resume codes for restarting Claude conversations with specialized context. Each agent section includes the resume command, the agent personality to adopt, and links to the documentation that agent should review when starting fresh.

> **Usage:** Copy the `claude --resume` command to continue an existing session, or start a new session and point the agent to the listed docs for onboarding context.
>
> **Updating:** Replace the resume ID when a session expires or you start a fresh one. Leave the line blank when no active session exists.
>
> **Agent Instructions:** Each session lists which agent personality file(s) from `~/.claude/agents/` to load. Read the primary agent file first to adopt its approach and priorities.
>
> **Required Reading:** Every agent should read the [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md) first for the full architecture overview.

## Table of Contents

- **Core Services** — [Focus Engine](#focus-engine) | [Game Engine](#game-engine)
- **AI / Data** — [AI Insights](#ai-insights) | [Analytics](#analytics)
- **Integrations** — [Music Control](#music-control)
- **Frontend** — [React UI](#react-ui)
- **Infrastructure** — [Docker & Config](#docker--config)
- [Cross-Cutting References](#cross-cutting-references) | [Agent Quick Reference](#agent-quick-reference)

---

## Core Services

### Focus Engine
```
claude --resume 708388d0-873d-42b3-a2d9-eec8f38be773
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-backend-architect.md`

**Codebase:**
- `services/focus_engine/` — Core timer & session management (port 8000)
- Models: session, user, base, response
- Routers: health, sessions, analytics, templates, websockets
- Services: session, analytics, focus scoring, notification, template, timer
- Database: connection, repositories, session repository

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md) — Architecture, patterns, code examples
- [Repository Structure Guide](/resources/docs/processes/repository-structure-guide.md)
- [Warp AI Agent Task List](/resources/docs/ai/warp-ai-agent-task-list.md)

**Key Patterns:**
- FastAPI with CORS middleware and lifespan management
- SQLAlchemy ORM with Pydantic validation
- WebSocket real-time updates (`/ws/session/{id}`)
- Multi-factor focus quality scoring algorithm
- Template system with 9+ presets and personalized recommendations
- Environment-driven config (Pydantic Settings, `FOCUS_FLOW_` prefix)

**Status:** Complete (Phase B2)

---

### Game Engine
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-backend-architect.md`

**Codebase:**
- `services/game_engine/` — Gamification system (port 8001)
- Models: achievements, levels, streaks, rewards
- Routers: achievements, levels, streaks, leaderboards (stubs)
- Services: achievement, level, streak, experience
- Calculators: experience, streak, difficulty
- Achievement modules: base, focus, milestone, streak

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md)

**Key Patterns:**
- Same FastAPI + SQLAlchemy patterns as focus engine
- XP calculator with difficulty modifiers
- Streak tracking with freeze/grace mechanics
- Achievement unlock system (focus, milestone, streak categories)

**Status:** Partial — models and calculators complete, routers need implementation

---

## AI / Data

### AI Insights
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-ai-engineer.md`
- Supporting: `~/.claude/agents/engineering/engineering-backend-architect.md`

**Codebase:**
- `services/ai_insights/` — AI-powered coaching and pattern discovery (port 8002)
- Models: analysis, insights, patterns
- Routers: insights, patterns, coaching (stubs)
- Services: session analyzer, pattern discoverer, coaching generator, correlation engine
- Clients: OpenAI, Ollama, analysis client
- `prompts/` — LLM prompt templates

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md)

**Key Patterns:**
- Dual LLM support: OpenAI API + local Ollama
- Prompt template system for coaching generation
- Session analysis and pattern discovery pipelines
- Correlation engine for productivity insights

**Status:** Partial — structure and models defined, analysis logic needs implementation

---

### Analytics
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-data-engineer.md`
- Supporting: `~/.claude/agents/engineering/engineering-backend-architect.md`

**Codebase:**
- `services/analytics/` — Productivity metrics and trend analysis (port 8003)
- Models: metrics, trends, comparisons
- Routers: metrics, trends, comparisons, export (stubs)
- Services: metrics calculator, trend analyzer, comparative analyzer, export
- Processors: session aggregator, time series, correlation

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md)

**Key Patterns:**
- Time-series processing for productivity trends
- Session aggregation and metric calculation
- Comparative analysis across time periods
- Data export service

**Status:** Partial — structure defined, processing logic needs implementation

---

## Integrations

### Music Control
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-backend-architect.md`

**Codebase:**
- `services/music_control/` — YouTube Music and Spotify integration (port 8004)
- Models: playlists, tracks, session music
- Routers: playlists, playback, discovery (stubs)
- Clients: YouTube Music (ytmusicapi), Spotify, browser control
- Services: playlist, focus detection, effectiveness tracker
- Utils: playlist analyzer, genre classifier

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md)

**Key Patterns:**
- YouTube Music API via `ytmusicapi` library
- Focus music effectiveness tracking per session
- Genre classification for playlist curation
- Browser control for playback

**Status:** Partial — structure and client stubs defined, API implementations needed

---

## Frontend

### React UI
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-frontend-developer.md`
- Supporting: `~/.claude/agents/design/design-ui-designer.md`

**Codebase:**
- `ui/focus-flow-app/` — React 19 + TypeScript frontend
- Components: layout (Header, Sidebar, Layout, Notifications), timer (Timer, TimerSettings, SessionHistory), ui (Button, Card, Input, Badge, Modal, LoadingSpinner, ConnectionStatus)
- Pages: Dashboard, Timer, Analytics, Templates, Settings, UIDemo
- Store: Redux Toolkit slices (session, timer, analytics, templates, ui)
- Services: base API (axios), session, analytics, templates, WebSocket
- Hooks: useWebSocket

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md) — React component patterns, hook examples

**Key Patterns:**
- React 19 + TypeScript strict mode
- Redux Toolkit with typed slices and selectors
- Tailwind CSS 4 for styling
- Vite 7 build tooling
- Axios-based API service layer
- WebSocket hook for real-time timer sync
- Reusable component library (10+ components)
- React Router 7 with 6 page routes

**Status:** Mostly complete (Phase B3) — needs integration with secondary services

---

## Infrastructure

### Docker & Config
```
claude --resume
```
**Agent Instructions:**
- Primary: `~/.claude/agents/engineering/engineering-devops-automator.md`

**Codebase:**
- `docker-compose.yml` — Local development (PostgreSQL, Redis, all services)
- `services/*/Dockerfile` — Per-service Docker images
- `services/*/requirements.txt` — Python dependencies
- `.env.example` — 26 environment variables (`FOCUS_FLOW_` prefix)
- `services/*/config/` — Per-service settings and logging config

**Docs:**
- [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md)
- [Repository Structure Guide](/resources/docs/processes/repository-structure-guide.md)

**Key Patterns:**
- Docker Compose for multi-service local dev
- Pydantic Settings for environment-driven config
- `FOCUS_FLOW_` prefix for all env vars
- Per-service Dockerfile with Python 3.11+
- Structured JSON logging via `logging_config.py`

---

## Cross-Cutting References

| Document | When to Review |
|----------|---------------|
| [LLM Project Knowledgebase](/resources/docs/ai/llm-project-knowledgebase.md) | Any work — architecture, patterns, code examples |
| [Repository Structure Guide](/resources/docs/processes/repository-structure-guide.md) | File placement, directory conventions |
| [Warp AI Agent Task List](/resources/docs/ai/warp-ai-agent-task-list.md) | Phase tracking, completed/planned tasks |
| [PROGRESS.md](/PROGRESS.md) | Current phase status |
| [.env.example](/.env.example) | Environment variables |
| [Product Brainstorm](/resources/brainstorming/product_brainstorm.md) | Product vision, weekly scheduling concept |
| [Technical Outline](/resources/brainstorming/technical-outline_brainstorm.md) | Architecture decisions |

## Agent Quick Reference

| Agent File | Session Areas |
|-----------|---------------|
| `engineering/engineering-backend-architect.md` | Focus Engine, Game Engine, Music Control, AI Insights (supporting), Analytics (supporting) |
| `engineering/engineering-ai-engineer.md` | AI Insights (primary — LLM integration, coaching, patterns) |
| `engineering/engineering-frontend-developer.md` | React UI (primary) |
| `engineering/engineering-data-engineer.md` | Analytics (primary — metrics, trends, time-series) |
| `engineering/engineering-devops-automator.md` | Docker & Config (primary) |
| `design/design-ui-designer.md` | React UI (supporting — component design, Tailwind) |

## Implementation Phase Tracker

| Phase | Scope | Status |
|-------|-------|--------|
| **A1** | Planning & architecture | Complete |
| **A2** | Infrastructure setup | Complete |
| **B1** | Database models & schemas | Complete |
| **B2** | Focus Engine (core service) | Complete |
| **B3** | Frontend foundation (React) | Mostly Complete |
| **B4** | Secondary services integration | Next Up |
| **C1** | Weekly scheduling features | Planned |
| **C2** | Multi-user & auth | Planned |
