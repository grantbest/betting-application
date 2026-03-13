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

## Agentic Operations
This project is managed by the **BestFam Agentic Toolkit** located in the `Homelab/meta/agents/` repository.
- `system-architect`: Designs boundaries and schemas.
- `homelab-manager`: Manages deployment and secrets.
- `betting-app-manager`: Handles code logic and rules.
