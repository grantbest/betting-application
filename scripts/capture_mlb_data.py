import statsapi as mlb
import json
import os
from datetime import datetime

# The date we want to capture for replaying
TARGET_DATE = "2024-09-29" 
DATA_DIR = "scripts/mock_api/data"

def capture_snapshot():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print(f"Capturing MLB Data for {TARGET_DATE}...")
    
    # 1. Teams
    print("Fetching teams...")
    teams = mlb.get('teams', {'sportId': 1})
    with open(f"{DATA_DIR}/teams.json", "w") as f:
        json.dump(teams, f)

    # 2. Schedule
    print(f"Fetching schedule for {TARGET_DATE}...")
    schedule = mlb.get('schedule', {'sportId': 1, 'date': TARGET_DATE})
    with open(f"{DATA_DIR}/schedule.json", "w") as f:
        json.dump(schedule, f)

    # 3. Game Feeds & Team Stats
    games = schedule.get('dates', [])[0].get('games', []) if schedule.get('dates') else []
    print(f"Found {len(games)} games. Fetching feeds and stats...")
    
    for game in games:
        g_id = game['gamePk']
        print(f"  -> Game {g_id}")
        
        # Feed
        feed = mlb.get('game', {'gamePk': g_id})
        with open(f"{DATA_DIR}/game_{g_id}.json", "w") as f:
            json.dump(feed, f)
            
        # Team Stats (for bullpen ranking)
        for side in ['away', 'home']:
            t_id = game['teams'][side]['team']['id']
            stats_path = f"{DATA_DIR}/stats_{t_id}.json"
            if not os.path.exists(stats_path):
                print(f"    -> Stats for team {t_id}")
                stats = mlb.get('team_stats', {
                    'teamId': t_id,
                    'season': 2024,
                    'group': 'pitching',
                    'stats': 'statSplits',
                    'sitCodes': 'rp'
                })
                with open(stats_path, "w") as f:
                    json.dump(stats, f)

    print(f"✅ Snapshot complete. Data saved to {DATA_DIR}")

if __name__ == "__main__":
    capture_snapshot()
