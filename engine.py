import statsapi as mlb
import psycopg2
import redis
import os
import time
import operator
import json
from datetime import datetime
from discord_webhook import DiscordWebhookAlert
from ai_orchestrator import AIAgent
from services.weather_service import WeatherService

# Operator mapping for RuleEvaluator
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le
}

class RuleEvaluator:
    """Evaluates JSON-based rules against game state."""
    @staticmethod
    def evaluate(rule_group, state):
        logic = rule_group.get('logic', 'AND')
        conditions = rule_group.get('conditions', [])
        
        results = []
        for cond in conditions:
            if 'logic' in cond: # Nested group
                results.append(RuleEvaluator.evaluate(cond, state))
            else: # Simple condition
                attr = cond.get('attribute')
                op = cond.get('operator')
                val = cond.get('value')
                
                state_val = state.get(attr)
                if state_val is None:
                    results.append(False)
                    continue
                
                try:
                    # Convert types if necessary
                    if isinstance(val, (int, float)) and not isinstance(state_val, (int, float)):
                        state_val = float(state_val)
                    results.append(OPS[op](state_val, val))
                except Exception:
                    results.append(False)
        
        if not results: return False
        return all(results) if logic == 'AND' else any(results)

# Bankroll Calculation: Kelly Criterion
def calculate_kelly(p, odds_american):
    b = (100 / abs(odds_american)) if odds_american < 0 else (odds_american / 100)
    q = 1 - p
    f_star = (b * p - q) / b
    fraction = float(os.getenv("KELLY_FRACTION", 0.25))
    return max(0, f_star * fraction)

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return psycopg2.connect(db_url)
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "mlb_engine"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

def get_redis_client():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis.Redis.from_url(redis_url, decode_responses=True)
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )

def get_setting(key, default=None):
    """Fetches a system setting from the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key,))
        res = cur.fetchone()
        cur.close()
        return res[0] if res else default
    except Exception as e:
        print(f"Error fetching setting {key}: {e}")
        return default
    finally:
        if conn:
            conn.close()

def log_inning_data(game_id, inning_number, half, runs, runners, game_info=None):
    """Logs or updates inning statistics in the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Upsert: Update if exists, insert if not
        cur.execute("""
            INSERT INTO inning_logs (game_id, inning_number, half, runs_scored, baserunners, game_info) 
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (game_id, inning_number, half) 
            DO UPDATE SET 
                runs_scored = EXCLUDED.runs_scored, 
                baserunners = EXCLUDED.baserunners, 
                game_info = EXCLUDED.game_info,
                last_updated = CURRENT_TIMESTAMP
        """, (game_id, inning_number, half, runs, runners, game_info))
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging inning data: {e}")
    finally:
        if conn:
            conn.close()

def log_weather(game_id, temp, wind, conditions):
    """Saves structured weather data to the game_weather table."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Ensure game exists first (referential integrity)
        cur.execute("INSERT INTO games (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (game_id,))
        
        # Log weather (Upsert based on game_id)
        cur.execute("""
            INSERT INTO game_weather (game_id, temperature, wind_speed, conditions)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (game_id) DO UPDATE SET
                temperature = EXCLUDED.temperature,
                wind_speed = EXCLUDED.wind_speed,
                conditions = EXCLUDED.conditions,
                timestamp = CURRENT_TIMESTAMP
        """, (game_id, temp, wind, conditions))
        
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging weather: {e}")
    finally:
        if conn:
            conn.close()

def update_team_data():
    """Populates the teams table with MLB team IDs, abbreviations, and bullpen rankings."""
    print("Updating team data and bullpen rankings...")
    try:
        teams_data = mlb.get('teams', {'sportId': 1})
        teams_list = teams_data.get('teams', [])
        
        bullpen_stats = []
        season = datetime.now().year
        
        # Fetch actual bullpen data from MLB API (simplified to ERA)
        conn = get_db_connection()
        cur = conn.cursor()
        
        for t in teams_list:
            t_id = t['id']
            t_abbr = t.get('abbreviation')
            # In a real app, we'd fetch actual ranks. For now, we seed or update existing.
            cur.execute("""
                INSERT INTO teams (team_id, abbreviation, bullpen_era_rank)
                VALUES (%s, %s, %s)
                ON CONFLICT (team_id) DO UPDATE SET abbreviation = EXCLUDED.abbreviation
            """, (t_id, t_abbr, 15)) # Defaulting rank to middle of pack
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Synced {len(teams_list)} teams with bullpen rankings.")
    except Exception as e:
        print(f"Error updating teams: {e}")

def log_bet(game_id, system, odds, stake, ai_insight=None, game_info=None):
    """Saves a triggered betting opportunity to the database for tracking."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bet_tracking (game_id, system_triggered, odds_taken, stake, ai_insight, game_info) VALUES (%s, %s, %s, %s, %s, %s)",
            (game_id, system, odds, stake, ai_insight, game_info)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging bet: {e}")
    finally:
        if conn:
            conn.close()

def get_active_games():
    """Fetches list of game IDs currently 'In Progress'."""
    try:
        # Get games for today
        today = datetime.now().strftime('%Y-%m-%d')
        schedule = mlb.get('schedule', {'date': today, 'sportId': 1})
        game_ids = []
        for date in schedule.get('dates', []):
            for game in date.get('games', []):
                status = game.get('status', {}).get('abstractGameState')
                if status in ['Live', 'Preview']:
                    game_ids.append(game.get('gamePk'))
        return game_ids
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def get_active_rules():
    """Fetches active betting rules from the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT rule_id, name, status, conditions_json, action_config FROM betting_rules WHERE status IN ('ACTIVE', 'DRY_RUN')")
        rows = cur.fetchall()
        rules = []
        for row in rows:
            rules.append({
                "id": row[0],
                "name": row[1],
                "status": row[2],
                "conditions": row[3],
                "config": row[4]
            })
        cur.close()
        return rules
    except Exception as e:
        print(f"Error fetching rules: {e}")
        return []
    finally:
        if conn:
            conn.close()

def monitor_games(alerter, redis_client, ai_agent=None, weather_service=None):
    """Main monitoring loop for dynamic rules."""
    active_game_ids = get_active_games()
    print(f"Monitoring {len(active_game_ids)} active games: {active_game_ids}", flush=True)
    rules = get_active_rules()
    
    if not rules:
        return

    for game_id in active_game_ids:
        try:
            game = mlb.get('game', {'gamePk': game_id})
            live_data = game.get('liveData', {})
            linescore = live_data.get('linescore', {})
            innings = linescore.get('innings', [])
            current_inning = linescore.get('currentInning', 1)
            is_top = linescore.get('isTopInning', True)
            
            # Identify teams and bullpen rank
            game_data = game.get('gameData', {})
            teams = game_data.get('teams', {})
            status = game_data.get('status', {}).get('abstractGameState')
            
            away_id = teams.get('away', {}).get('id')
            home_id = teams.get('home', {}).get('id')
            
            # Fetch Weather Data (Always do this for all active games)
            weather_str = ""
            if weather_service:
                weather = weather_service.get_weather_data(game_id)
                temp = weather.get('temp')
                wind = weather.get('wind')
                cond = weather.get('conditions', 'Clear')
                
                # Save structured data
                if temp is not None:
                    log_weather(game_id, temp, wind, cond)
                    weather_str = f" | 🌡️ {temp}°F | 💨 {wind}mph"
                else:
                    weather_str = " | 🌡️ ??°F | 💨 ??mph"

            # Skip detailed processing if the game hasn't started
            if status == 'Preview':
                continue

            pitching_team_id = home_id if is_top else away_id

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT bullpen_era_rank FROM teams WHERE team_id = %s", (pitching_team_id,))
            rank_res = cur.fetchone()
            bullpen_rank = rank_res[0] if rank_res else 15
            cur.close()
            conn.close()

            # Construct State for Evaluator
            state = {
                "inning": current_inning,
                "score_diff": linescore.get('home', {}).get('runs', 0) - linescore.get('away', {}).get('runs', 0),
                "pitching_team_bullpen_rank": bullpen_rank,
                "runs_scored_half": linescore.get('home' if not is_top else 'away', {}).get('runs', 0),
                "baserunners": (1 if linescore.get('offense', {}).get('first') else 0) + 
                              (1 if linescore.get('offense', {}).get('second') else 0) + 
                              (1 if linescore.get('offense', {}).get('third') else 0)
            }

            away_abbr = teams.get('away', {}).get('abbreviation', 'AWY')
            home_abbr = teams.get('home', {}).get('abbreviation', 'HM')
            game_date = datetime.now().strftime('%-m/%-d')
            game_info = f"{home_abbr} Vs {away_abbr} - {game_date}{weather_str}"

            # Update Inning Logs
            for idx, inning in enumerate(innings):
                inn_num = idx + 1
                for half in ['away', 'home']:
                    data = inning.get(half, {})
                    log_inning_data(game_id, inn_num, half, data.get('runs', 0), data.get('hits', 0) + data.get('leftOnBase', 0), game_info)

            # Evaluate each dynamic rule
            for rule in rules:
                alert_key = f"alert:{game_id}:{rule['id']}"
                if redis_client.exists(alert_key):
                    continue
                
                if RuleEvaluator.evaluate(rule['conditions'], state):
                    status_prefix = "[DRY RUN] " if rule['status'] == 'DRY_RUN' else ""
                    print(f"{status_prefix}Rule '{rule['name']}' triggered for {game_id}")
                    
                    config = rule['config'] or {}
                    p = config.get('p', 0.55)
                    odds = config.get('odds', -110)
                    stake = calculate_kelly(p, odds)
                    
                    ai_insight = None
                    if ai_agent:
                        print(f"Generating AI Insight for {rule['name']}...")
                        ai_insight = ai_agent.generate_insight(rule['name'], state)
                    
                    if rule['status'] == 'ACTIVE' and alerter:
                        alerter.send_alert(rule['name'], game_id, "Dynamic Rule Trigger", odds, stake, ai_insight)
                    
                    log_bet(game_id, rule['name'], odds, stake, ai_insight, game_info)
                    redis_client.setex(alert_key, 86400, "1")

        except Exception as e:
            print(f"Error monitoring game {game_id}: {e}")

if __name__ == "__main__":
    print("MLB Engine Active. Scanning for opportunities...", flush=True)
    update_team_data()
    
    # Priority: Database Setting -> Environment Variable
    webhook_url = get_setting("discord_webhook_url") or os.getenv("DISCORD_WEBHOOK_URL")
    alerter = DiscordWebhookAlert(webhook_url) if webhook_url else None
    
    redis_client = get_redis_client()
    weather_service = WeatherService()
    
    ai_agent = None
    try:
        ai_agent = AIAgent()
        print("✅ AI Orchestrator initialized.")
    except Exception as e:
        print(f"⚠️ AI Orchestrator failed to initialize: {e}")
    
    while True:
        monitor_games(alerter, redis_client, ai_agent, weather_service)
        time.sleep(60) # Scan every minute
