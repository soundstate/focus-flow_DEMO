# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Focus Flow is an interactive productivity timer with gamification, built as a microservices product. Active development — backend services and frontend foundations are scaffolded and tested. The project tracks phase-by-phase progress in `PROGRESS.md`; consult it before starting work to see what's done and what's next.

**Tech stack:** FastAPI (Python), PostgreSQL, Redis, React + TypeScript, WebSockets, Docker.

**Service breakdown:** five microservices — `focus_engine`, `gamification`, `analytics`, `ai_insights`, `music_control` — each in its own folder under `services/`.

## Required Reading Before Starting Any Task

- `README.md` — product framing.
- `PROGRESS.md` — authoritative tracker for what's complete and what's next. Read this first; do not assume earlier phases are unfinished.
- `docs/` — technical notes per service.

## Repository Structure

```
focus-flow_DEMO/
├── services/         # Five microservices (focus_engine, gamification, analytics, ai_insights, music_control)
├── ui/               # React + TypeScript frontend
├── docs/             # Technical notes
├── resources/        # Shared assets and reference material
├── docker-compose.yml
├── pytest.ini
└── PROGRESS.md       # Phase tracker (authoritative)
```

## Conventions

- Each service is independently testable. Run service-specific pytest from the service's root before touching shared code.
- Update `PROGRESS.md` immediately when completing a tracked task. Don't let it lag behind real state.
- Frontend and backend are coupled via REST + WebSockets. Test both sides when changing a contract.

## Cowork workstation

This repo routes to the `side-products` workstation in `O:\_cowork-os\03_workstations\side-products\` for product-strategy work (specs, positioning, brainstorm). In-repo coding work stays here.
