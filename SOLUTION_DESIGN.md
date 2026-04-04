# MLB Betting Engine v2.0: "The Quant-First Evolution"

## 1. Executive Summary
The goal of this iteration is to transition from a **Rule-Driven** system (V1) to a **Reasoning-Driven** system (V2). By leveraging **Gemma 4** as the "Strategy Brain" and **DuckDB** as the "Memory Bank," the engine will not only trigger on rules but will deliberate on the *value* of each bet using historical performance and real-time situational analysis.

---

## 2. Core Architecture Components

### A. The "Lynchpin": Gemma 4 (via Ollama)
Gemma 4 (specifically the **26B MoE** or **31B Dense** versions) will serve as the primary decision-maker.
- **Thinking Mode:** Native `<|think|>` channel will be used for "Chain of Thought" strategy deliberation.
- **Role:** 
    - Analyzes live game state + historical context retrieved from DuckDB.
    - Generates a "Model Win Probability" ($P_{model}$).
    - Calculates the "Edge" against bookmaker implied probability ($P_{implied}$).
    - Explains the reasoning (e.g., "Home pitcher ERA rises 22% in temps >85°F; bullpen is gassed from yesterday's 14-inning game").

### B. The "Memory Bank": DuckDB + Parquet
A high-performance, local OLAP database for quantitative research.
- **Storage:** Compressed **Apache Parquet** files stored locally (e.g., `data/historical_mlb_2015_2025.parquet`).
- **Function:** 
    - Performs ultra-fast "Similarity Searches" (e.g., "In the last 10 years, how often has a team down by 2 in the 7th at Coors Field won?").
    - Provides historical batting/pitching stats that the live API lacks (e.g., advanced Statcast metrics like Exit Velocity or Barrel %).
- **Reasoning:** In-process, no server needed, extremely fast on Apple Silicon.

### C. The "Framework": `sports-betting` (Python)
Integrate the [georgedouzas/sports-betting](https://github.com/georgedouzas/sports-betting) framework to standardize the quant workflow.
- **Dataloaders:** Standardized ingestion of historical odds and results.
- **Backtester:** Simulates strategies over historical seasons to calculate ROI and drawdown.

---

## 3. Data Flow & Execution Pipeline

1.  **Ingestion:** `engine.py` polls MLB Stats API for live game state and weather.
2.  **Trigger (System 1):** Fast rules (e.g., "Score is tied, 8th inning") identify a *potential* opportunity.
3.  **Contextualization:** The `QuantEngine` queries **DuckDB** for historical scenarios matching the current game state (weather, teams, ballpark).
4.  **Deliberation (System 2):** 
    - **Prompt:** Gemma 4 receives [Live State + Historical Context + Bookie Odds].
    - **Thinking:** Gemma 4 uses `<|think|>` to deliberate.
    - **Output:** Recommendation (BET/NO BET) + Estimated Fair Odds.
5.  **Risk Management:** If BET is recommended, use the **Kelly Criterion** (via `WagerBrain`) to calculate the optimal fraction of the bankroll.
6.  **Logging:** All AI "thoughts" and reasoning are logged into PostgreSQL for later audit.

---

## 4. Implementation Strategy (The "Polecat" Roadmap)

### Phase 1: Data Infrastructure
- [ ] Initialize local DuckDB instance in `BettingApp/data/`.
- [ ] Script to convert historical MLB CSVs (Retrosheet/Statcast) into local Parquet files.
- [ ] Update `requirements.txt` with `duckdb`, `polars`, `sports-betting`.

### Phase 2: Gemma 4 Integration
- [ ] Pull `gemma4:26b` in Ollama.
- [ ] Rewrite `AIAgent` to support the `<|think|>` channel for strategy deliberation.
- [ ] Develop a "Strategy Prompt Template" that forces Gemma 4 to compare historical win probabilities from DuckDB against live lines.

### Phase 3: Quant Engine Development
- [ ] Create `quant_engine.py` to orchestrate the "Retrieve-Reason-Act" loop.
- [ ] Implement "Similarity Search" in SQL (DuckDB) to provide context to Gemma 4.
- [ ] Integrate `WagerBrain` for advanced bankroll math (removing "vig" and calculating fair price).

---

## 5. Security & Safety
- **Local-First:** All reasoning and data analysis stays on the MacBook. No sensitive bet data or API keys sent to cloud providers.
- **Audit Logs:** Every "Thinking" trace is stored locally to verify the AI isn't "hallucinating" its confidence.
