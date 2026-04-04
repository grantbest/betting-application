# MLB Quant Engine v2.0: Feature Roadmap & UI Refactor

With the integration of the Gemma 4 Reasoning Engine and the DuckDB Parquet Data Lake, the BettingApp must evolve from a simple monitoring dashboard into a professional Quantitative Analysis Terminal. 

Here are the top use-cases and the corresponding features we need to implement in the Next.js frontend and Python backend.

## 1. Traceability: The "Explainable Edge"
Quant analysts need to trust the system. If the AI recommends a bet, the analyst must be able to trace exactly *why* that recommendation was made.

**New Features:**
*   **The "Thinking Trace" Viewer:** 
    *   *Backend:* Ensure `ai_orchestrator.py` captures and stores the raw `<|thought|>` output from Gemma 4 in the `bet_tracking` table.
    *   *Frontend:* A new UI modal on the dashboard that expands a bet to show Gemma 4's step-by-step reasoning.
*   **Similarity Context Audit:**
    *   *Feature:* Display the exact historical vector that DuckDB returned (e.g., "Found 43 similar games: 56% Home Win Rate") alongside the bet.
*   **Closing Line Value (CLV) Tracking:**
    *   *Feature:* Track the odds at the time of the bet vs. the final closing odds before the first pitch. A positive CLV means the system is finding true edge, regardless of the individual game's outcome.

## 2. Data Visualization: "Seeing the Value"
Raw numbers are hard to parse in real-time. The UI needs to visually highlight discrepancies between the market and our model.

**New Features:**
*   **The "Edge" Heatmap:**
    *   *Feature:* A scatter plot visualizing active games. X-axis: Bookmaker Implied Probability. Y-axis: Gemma 4 Model Probability. Games above the diagonal line represent "Value" (Edge).
*   **Strategy Backtest Visualization:**
    *   *Feature:* A time-series chart showing simulated bankroll growth over time based on historical DuckDB backtests, visualizing drawdowns and win streaks.

## 3. Multi-Dimensional Rule Engine (The "Strategy Builder")
The old rules engine only looked at the current inning and score. The V2 engine must support complex, multi-dimensional queries across the new data lake.

**New Features:**
*   **Advanced Rule Builder UI:** Upgrade the `/rules` page to support group logic (AND/OR) across new dimensions:
    *   *Weather Vector:* `Wind Direction == 'OUT'` AND `Wind Speed > 10mph` AND `Temp > 80F` (Identifies high-scoring environments).
    *   *Fatigue Vector:* `Pitching Team Bullpen Innings (Last 3 Days) > 12`.
    *   *Matchup Vector:* `Starting Pitcher ERA vs Lefties > 4.5` AND `Opposing Lineup LHB Count >= 5`.
*   **"Dry Run" Backtester:**
    *   *Feature:* Before a rule goes "ACTIVE", allow the user to run it against the DuckDB historical dataset. The UI should instantly report: "If this rule was active in March 2026, it would have triggered 14 times with an ROI of +12%."

## 4. Execution Plan (via Gastown)
We will leverage the Gastown Orchestrator to implement these features using Temporal workflows and Beads:

1.  **Epic 1: Traceability Infrastructure**
    *   *Bead:* Update Postgres schema for `bet_tracking` to include `gemma_trace` and `clv`. Update `QuantEngine` to calculate CLV.
2.  **Epic 2: The Quant Dashboard (Frontend)**
    *   *Bead:* Refactor Next.js dashboard. Add Recharts/Chart.js for the Edge Heatmap. Build the "Thinking Trace" modal.
3.  **Epic 3: The Multi-Dimensional Engine**
    *   *Bead:* Build the Advanced Rule Builder UI and wire it to a new backtesting API endpoint that queries DuckDB.
