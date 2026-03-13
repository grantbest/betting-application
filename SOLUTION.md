# MLB Betting Engine: Solution Blueprint v1.1
## Real-time Quantitative Analytics & AI-Driven Wagering Insights

### Executive Summary
The **MLB Betting Engine** is a high-performance, containerized analytics platform designed to identify high-probability betting opportunities in Major League Baseball games. By integrating real-time game data with dynamic statistical modeling and a local Agentic AI layer, the system provides automated, data-driven insights and bankroll management (Kelly Criterion) delivered directly via Discord.

---

### 1. Core Solution Scope
The engine operates at the intersection of three domains:
*   **Real-time Ingestion:** Continuous monitoring of live MLB game states (innings, counts, baserunners, and pitcher/batter matchups).
*   **Quantitative Analysis:** Application of complex betting logic (e.g., NR2I, Big Inning Momentum) through a JSON-based dynamic rules engine.
*   **Bankroll Optimization:** Automated stake calculation using the Kelly Criterion to maximize long-term growth while mitigating risk.

---

### 2. Architectural Overview
The system employs a decoupled, 4-tier microservices architecture for maximum stability and scalability.

#### **A. Ingestion & Execution (Python 3.11 Engine)**
The "brain" of the operation. It leverages `asyncio` for non-blocking game polling and `mlb-statsapi` for high-fidelity data.
*   **Dynamic Rules Engine:** Decouples betting logic from source code, allowing for real-time strategy updates via JSON-formatted conditions.
*   **State Machine:** Maintains an in-memory representation of every active MLB game to detect momentum shifts instantly.

#### **B. Agentic AI Layer (Ollama + Llama3)**
A local AI orchestration layer provides qualitative depth to quantitative triggers.
*   **Insight Agent:** Generates natural-language justifications for every alert, explaining *why* a bet is statistically sound (e.g., "Bullpen ERA mismatch in the 7th inning").
*   **Optimization Agent:** Analyzes historical PostgreSQL data to propose JSON rule modifications, closing the feedback loop between data and strategy.

#### **C. Persistence & Messaging (PostgreSQL & Redis)**
*   **PostgreSQL 15:** Stores historical inning logs, team rankings (updated daily), and a full audit trail of every bet placed.
*   **Redis 7:** Facilitates real-time messaging and state caching, ensuring the engine can scale horizontally across multiple game-day instances.

#### **D. Delivery & Visualization (Next.js & Discord)**
*   **Next.js Dashboard:** A modern React frontend for real-time monitoring of engine health, active rules, and historical performance.
*   **Discord Webhooks:** Rich-embed notifications providing actionable data, AI insights, and calculated stakes directly to the user.

---

### 3. Key Features & Technical Moats
*   **No-Toil Re-paving:** Integrated `docker-entrypoint.sh` automates database schema migrations and service discovery. If the infrastructure is wiped, the system self-heals and re-initializes on startup.
*   **Environment Agnostic:** Support for both individual environment variables (`DB_HOST`, `REDIS_HOST`) and unified connection strings (`DATABASE_URL`, `REDIS_URL`), ensuring seamless portability between local development, Homelab, and cloud production.
*   **Local AI Privacy:** By hosting **Ollama** within the infrastructure, all analytical reasoning remains local, incurring zero API costs and zero data leakage.
*   **Mock-Driven Development:** A dedicated `mock_api` service simulates game-day traffic, allowing for exhaustive strategy backtesting without hitting rate limits or waiting for live games.

---

### 4. Deployment & GitOps
The project follows a **Build Once, Run Anywhere** philosophy:
*   **CI/CD:** GitHub Actions build and push branch-specific images (`dev` vs `prod`) to GHCR.
*   **Infrastructure-as-Code:** Docker Compose orchestrates the entire stack, with environment-specific overrides for mock vs. live data.
*   **Automated Validation:** Integrated preflight checks ensure that logic changes, type safety (TypeScript), and database integrity are verified before any deployment.

---

### 5. Future Roadmap
*   **Predictive Bullpen Exhaustion:** Integrating pitch-count tracking to predict late-inning scoring surges.
*   **Automated Backtesting Suite:** A tool to run historical seasons through the rules engine to calculate theoretical ROI.
*   **Multi-Bookie Odds Comparison:** Expanding the ingestion layer to include real-time odds from multiple sportsbooks.

---
*Developed by WE do it inc.*
*Last Updated: Friday, March 13, 2026 (CI/CD Pipeline Test v1.1)*
