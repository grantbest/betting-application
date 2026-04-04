import asyncio
import duckdb
import polars as pl
import statsapi as mlb
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Paths
DATA_DIR = Path("/Users/grantbest/Documents/Active/BettingApp/data")
GOLD_DIR = DATA_DIR / "gold"

from services.weather_service import WeatherService

async def backfill_range(start_date_str: str, end_date_str: str):
    """Backfills MLB game data for a range of dates."""
    ws = WeatherService()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    
    current_date = start_date
    total_ingested = 0
    
    db_path = DATA_DIR / "mlb_quant.db"
    conn = duckdb.connect(str(db_path))

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"📥 Processing {date_str}...")
        
        try:
            # Fetch from MLB API
            schedule = mlb.get('schedule', {'date': date_str, 'sportId': 1})
            games_list = []
            
            for date_data in schedule.get('dates', []):
                for game in date_data.get('games', []):
                    # We only care about Final games for historical analysis
                    game_id = game.get('gamePk')
                    status = game.get('status', {}).get('abstractGameState')
                    
                    # Fetch weather for this game
                    weather = ws.get_weather_data(game_id)
                    
                    games_list.append({
                        "game_id": game_id,
                        "date": date_str,
                        "home_team": game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
                        "away_team": game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
                        "status": status,
                        "home_score": game.get('teams', {}).get('home', {}).get('score', 0),
                        "away_score": game.get('teams', {}).get('away', {}).get('score', 0),
                        "temperature": weather.get('temp'),
                        "wind_speed": weather.get('wind'),
                        "wind_direction": weather.get('wind_direction')
                    })
            
            if games_list:
                df = pl.DataFrame(games_list)
                output_path = GOLD_DIR / f"games_{date_str}.parquet"
                df.write_parquet(output_path)
                
                conn.execute(f"INSERT INTO meta_log (event) VALUES ('Backfilled {len(games_list)} games for {date_str}')")
                total_ingested += len(games_list)
                print(f"  ✅ Saved {len(games_list)} games.")
            else:
                print(f"  ⚠️ No games found for {date_str}.")
                
        except Exception as e:
            print(f"  ❌ Failed for {date_str}: {e}")
            
        current_date += timedelta(days=1)
    
    conn.close()
    print(f"\n✨ Backfill Complete! Total games ingested: {total_ingested}")

if __name__ == "__main__":
    # Default to March 2026 (Spring Training + Start of Season)
    start = "2026-03-01"
    end = "2026-03-31"
    
    if len(sys.argv) == 3:
        start = sys.argv[1]
        end = sys.argv[2]
        
    asyncio.run(backfill_range(start, end))
