# CLAUDE.md

> **Cross-cutting AI workflow lives in workbench (Notion).** Personalization system at [workbench / cowork-os](https://www.notion.so/357b4cf4526e814fb4c9e7d23fd52d2f) (voice + writing + identity + engineering + agent routing + notion rules). AI tool routing + cross-cutting development principles at [workbench / ai-workflow](https://www.notion.so/363b4cf4526e8176bc0be9535bf64e8a). Per-Claude-product detail at [workbench / claude](https://www.notion.so/365b4cf4526e81c79ccbc8c5f7b4df8f). Universal coding-rule skillsets at [workbench / custom-skillsets](https://www.notion.so/365b4cf4526e81ac80b9c056e527b8b9). Agent-personality catalog at [workbench / agent-personalities](https://www.notion.so/363b4cf4526e81c88ef2f9101fd51252).
>
> This file holds rules **specific to this repo**. Edits to cross-cutting AI guidance should land in Notion first; edits to repo-specific rules land here.

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Focus Flow is an interactive productivity timer with gamification, built as a microservices product. Active development — backend services and frontend foundations are scaffolded and tested. The project tracks phase-by-phase progress in `PROGRESS.md`; consult it before starting work to see what's done and what's next.

**Tech stack:** FastAPI (Python), PostgreSQL, Redis, React + TypeScript, WebSockets, Docker.

**Service breakdown:** five microservices — `focus_engine`, `game_engine`, `analytics`, `ai_insights`, `music_control` — each in its own folder under `services/`.

## Required Reading Before Starting Any Task

- `README.md` — product framing.
- `PROGRESS.md` — authoritative tracker for what's complete and what's next. Read this first; do not assume earlier phases are unfinished.
- `docs/` — technical notes per service.

## Repository Structure

```
focus-flow_DEMO/
├── services/         # Five microservices (focus_engine, game_engine, analytics, ai_insights, music_control)
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
