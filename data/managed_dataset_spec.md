# MLB Quant Managed Dataset Spec v2.0

This specification defines the local data structure for the "Memory Bank" (DuckDB). This dataset is managed by the **Gastown Ingestion Pipeline** and is optimized for ultra-fast "Similarity Searches" and Gemma 4 reasoning.

---

## 1. Directory Structure (`BettingApp/data/`)

```text
data/
├── raw/            # Daily MLB Stats API JSON dumps (immutable)
├── bronze/         # Normalized CSVs (Historical Retrosheet/Statcast)
├── gold/           # Production Parquet files (Partitioned by Season)
│   ├── games.parquet
│   ├── pitches.parquet
│   └── boxscores.parquet
└── mlb_quant.db    # Persistent DuckDB Database File
```

---

## 2. Core Schema (The "Reasoning Context")

### A. `games_historical` (Parquet)
Used by Gemma 4 to find "similar situations."
- `game_id`: (Primary Key)
- `date`: (ISO Date)
- `home_team`: (Abbr)
- `away_team`: (Abbr)
- `ballpark`: (Name/ID)
- `temperature`: (Decimal)
- `wind_speed`: (Decimal)
- `wind_direction`: (Categorical: IN, OUT, L-to-R)
- `total_runs`: (Outcome)
- `win_prob_7th`: (Calculated historical probability)

### B. `pitcher_splits` (Calculated Feature Table)
Aggregated from `pitches.parquet` for real-time inference.
- `pitcher_id`
- `era_vs_lhb` / `era_vs_rhb`
- `avg_exit_velo_last_10`
- `rest_days`: (Days since last appearance)

---

## 3. Gastown Bead Integration

### Bead: `INGEST_DAILY_DATA`
- **Source:** MLB Stats API
- **Target:** `data/raw/` -> `data/gold/games.parquet`
- **Validation:** Total game count must match the day's schedule.

### Bead: `CALCULATE_SIMILARITY_CONTEXT`
- **Input:** Live Game Vector: `[Inning, Score, Outs, Runners, Ballpark, Weather]`
- **Action:** DuckDB `SELECT` for top 50 historically similar games.
- **Output:** JSON summary passed to Gemma 4 for deliberation.

---

## 4. Why this works for a Quant Analyst
1.  **Zero-ETL:** DuckDB queries the Parquet files directly. No "Loading" time.
2.  **Versioning:** Parquet files are versioned by season. You can "Roll back" to a previous season's rank logic easily.
3.  **Local-First:** All Statcast/Pitch-level data (millions of rows) stays on the MacBook SSD.
