import asyncio
import duckdb
import polars as pl
import statsapi as mlb
from datetime import datetime, timedelta
from temporalio import activity, worker
from pathlib import Path

# Paths
DATA_DIR = Path("/Users/grantbest/Documents/Active/BettingApp/data")
GOLD_DIR = DATA_DIR / "gold"

@activity.defn
async def ingest_mlb_daily_activity(date_str: str) -> str:
    """Fetches MLB game data for a specific date and saves to Parquet."""
    try:
        print(f"🚀 Gastown Activity: Ingesting data for {date_str}...")
        
        # 1. Fetch from MLB API
        schedule = mlb.get('schedule', {'date': date_str, 'sportId': 1})
        games_list = []
        
        for date in schedule.get('dates', []):
            for game in date.get('games', []):
                games_list.append({
                    "game_id": game.get('gamePk'),
                    "date": date_str,
                    "home_team": game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
                    "away_team": game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
                    "status": game.get('status', {}).get('abstractGameState'),
                    "home_score": game.get('teams', {}).get('home', {}).get('score', 0),
                    "away_score": game.get('teams', {}).get('away', {}).get('score', 0)
                })
        
        if not games_list:
            return f"No games found for {date_str}"

        # 2. Convert to Polars DataFrame
        df = pl.DataFrame(games_list)
        
        # 3. Save to Parquet (Partitioned by Date)
        output_path = GOLD_DIR / f"games_{date_str}.parquet"
        df.write_parquet(output_path)
        
        # 4. Update DuckDB Meta Log
        db_path = DATA_DIR / "mlb_quant.db"
        conn = duckdb.connect(str(db_path))
        conn.execute(f"INSERT INTO meta_log (event) VALUES ('Ingested {len(games_list)} games for {date_str}')")
        conn.close()
        
        return f"Successfully ingested {len(games_list)} games to {output_path}"
    
    except Exception as e:
        raise Exception(f"Ingestion failed: {str(e)}")

async def main():
    # In a real Gastown setup, this would connect to the central Temporal server
    # For local dev/test, we run a local worker
    client = await worker.Worker.connect("localhost:7233")
    
    # Registering the worker on the 'betting-app-queue'
    ingest_worker = worker.Worker(
        client,
        task_queue="betting-app-queue",
        activities=[ingest_mlb_daily_activity]
    )
    
    print("🐝 Gastown Ingestion Worker active. Waiting for Beads...")
    await ingest_worker.run()

if __name__ == "__main__":
    asyncio.run(main())
