# WE do it inc. | MLB Betting Engine v1.2.0

## Core Design
- **Architecture:** Microservices-first (Engine + Frontend + Mock API).
- **Data Model:** Clean 3rd Normal Form (3NF) in PostgreSQL.
- **Rules Engine:** JSON-based dynamic strategies.
- **AI Insights:** Local Ollama integration for strategy reasoning.

## GitOps & CI/CD
- **Code:** `BettingApp` repository.
- **Control:** `Homelab` repository (GitOps Control Plane).
- **Registry:** GHCR (`ghcr.io/grantbest/betting-application/`).
- **Important:** The prod engine previously used a stale GHCR image (`engine:main`). As of 2026-03-19, both prod and dev build the engine locally from source. Do NOT revert to `image: ghcr.io/...` for the engine — it contains an outdated `WeatherService` that hits a non-existent external API.

## Known Issues Fixed (2026-03-19)
- **`/rules` nav link** was pointing to `/health` in `page.tsx`. Fixed.
- **`/health` and `/chat` pages** used inline `S` style objects instead of Tailwind CSS. Rewritten to match the app-wide dark slate design system.
- **`game_info` NULL in prod bets** — `init_db.py` seed INSERT omitted the `game_info` column. Fixed: seed data now includes `game_info` with weather strings. Existing prod rows backfilled directly.
- **Prod engine stale image** — `betting-prod/docker-compose.yml` used `image: ghcr.io/.../engine:main` which had an outdated `WeatherService` (hit `api.weatherprovider.com`, always returned defaults). Changed to `build: context: ../../../BettingApp` to build from local source. Engine now uses MLB Stats API directly for weather (no API key needed).

## WeatherService
- Fetches weather from `game.liveData.boxscore.info` via the MLB Stats API using `game_id`.
- No external API key required.
- Fallback: `72°F / 5mph / Clear` on error.

## Agentic Operations
This project is managed by the **BestFam Agentic Toolkit** located in the `Homelab/meta/agents/` repository.
- `system-architect`: Designs boundaries and schemas.
- `homelab-manager`: Manages deployment and secrets.
- `betting-app-manager`: Handles code logic and rules.
