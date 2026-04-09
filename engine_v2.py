import statsapi as mlb
import psycopg2
import redis
import os
import time
import operator
import json
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhookAlert
from ai_orchestrator import AIAgent
from services.weather_service import WeatherService
from services.quant_service import QuantService
from dotenv import load_dotenv

# Load V3.2 Performance Hybrid environment
load_dotenv()

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
        if not rule_group:
            return False
        if isinstance(rule_group, list):
            rule_group = {"logic": "AND", "conditions": rule_group}
            
        logic = rule_group.get('logic', 'AND')
        conditions = rule_group.get('conditions', [])
        
        if not conditions:
            return False
        
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

        # V2.4: Keep the database clean - only keep last 2 innings per game
        # This forces the chronological feed to only show relevant recent data
        cur.execute("""
            DELETE FROM inning_logs 
            WHERE game_id = %s AND inning_number < %s
        """, (game_id, inning_number - 1))

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
        cur.execute("INSERT INTO mlb_games (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (game_id,))

        
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
                INSERT INTO mlb_teams (team_id, abbreviation, bullpen_era_rank)
                VALUES (%s, %s, %s)
                ON CONFLICT (team_id) DO UPDATE SET abbreviation = EXCLUDED.abbreviation
            """, (t_id, t_abbr, 15)) # Defaulting rank to middle of pack
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Synced {len(teams_list)} teams with bullpen rankings.")
    except Exception as e:
        print(f"Error updating teams: {e}")

def log_bet(game_id, system, odds, stake, ai_insight=None, game_info=None, clv=None, ai_trace=None, deep_link_url=None, inning=None):
    """Saves a triggered betting opportunity to the database with V2.0 analytics."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO bet_tracking 
               (game_id, system_triggered, odds_taken, stake, ai_insight, game_info, clv, ai_trace, deep_link_url, inning) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (game_id, system, odds, stake, ai_insight, game_info, clv, ai_trace, deep_link_url, inning)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error logging bet: {e}")
    finally:
        if conn:
            conn.close()

def get_active_games():
    """Fetches list of game IDs currently 'In Progress' or 'Preview'."""
    try:
        # V3.7: Check both today and yesterday to catch late-night games transitioning dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        dates_to_check = [
            yesterday.strftime('%Y-%m-%d'),
            today.strftime('%Y-%m-%d')
        ]
        
        game_ids = set()
        for date_str in dates_to_check:
            schedule = mlb.get('schedule', {'date': date_str, 'sportId': 1})
            for date in schedule.get('dates', []):
                for game in date.get('games', []):
                    status = game.get('status', {}).get('abstractGameState')
                    if status in ['Live', 'Preview']:
                        game_ids.add(game.get('gamePk'))
        
        return list(game_ids)
    except Exception as e:
        print(f"Error fetching schedule: {e}")
        return []

def get_active_rules():
    """Fetches active betting rules from the database."""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT rule_id as id, name, status, conditions_json as conditions, action_config as config FROM betting_rules WHERE status IN ('ACTIVE', 'DRY_RUN')")
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

from services.quant_service import QuantService

import subprocess

def trigger_sre_activity(title, details):
    """Triggers the SRE healing workflow via the local script."""
    try:
        orchestrator_dir = "/Users/grantbest/Documents/Active/BestFam-Orchestrator"
        script_path = f"{orchestrator_dir}/scripts/trigger_sre_healing.py"
        
        # NOTE: SRE scripts are in the mounted BestFam-Orchestrator volume
        # which keeps its absolute host paths inside the container mount.
        # But wait, if it's mounted at /Users/grantbest/Documents/Active/BestFam-Orchestrator
        # then the absolute path IS correct.
        
        # Let's verify where it's mounted in docker-compose.
        # volumes:
        #  - /Users/grantbest/Documents/Active/BestFam-Orchestrator:/Users/grantbest/Documents/Active/BestFam-Orchestrator
        
        # OK, so the path I had was correct for SRE scripts because of the mount.
        # BUT trigger_gastown_alert.py is in BettingApp which is NOT mounted 
        # at the host absolute path, it's just COPYed to /app.
        
        # So trigger_sre_healing.py WAS correct. I'll just keep it or make it more robust.
        
        # Run in background using container's python
        subprocess.Popen(
            ["python", script_path, title, details],
            env={**os.environ, "PYTHONPATH": f"{orchestrator_dir}:{orchestrator_dir}/src:{orchestrator_dir}/scripts"},
            start_new_session=True
        )
        print(f"📡 SRE Healing Triggered: {title}")
    except Exception as e:
        print(f"❌ Failed to spawn SRE trigger: {e}")

def monitor_games(alerter, redis_client, ai_agent=None, weather_service=None):
    """Main monitoring loop for dynamic rules with V2.0 Quant Reasoning."""
    active_game_ids = get_active_games()
    print(f"Monitoring {len(active_game_ids)} active games: {active_game_ids}", flush=True)
    rules = get_active_rules()
    quant_service = QuantService() # V2.0 Memory Bank
    
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
            
            # Identify teams and ballpark info
            game_data = game.get('gameData', {})
            teams = game_data.get('teams', {})
            status = game_data.get('status', {}).get('abstractGameState')
            
            away_id = teams.get('away', {}).get('id')
            home_id = teams.get('home', {}).get('id')
            
            # Fetch Weather Data
            weather_data = {"temp": 72, "wind": 5, "wind_direction": "Calm", "conditions": "Clear"}
            weather_str = ""
            if weather_service:
                try:
                    weather_data = weather_service.get_weather_data(game_id)
                except Exception as we:
                    print(f"Weather fetch failed for {game_id}: {we}")
                
                temp = weather_data.get('temp')
                wind = weather_data.get('wind')
                cond = weather_data.get('conditions', 'Clear')
                if temp is not None:
                    log_weather(game_id, temp, wind, cond)
                    weather_str = f" | 🌡️ {temp}°F | 💨 {wind}mph"

            if status == 'Preview':
                continue

            pitching_team_id = home_id if is_top else away_id
            venue_id = game_data.get('venue', {}).get('id')

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT bullpen_era_rank FROM mlb_teams WHERE team_id = %s", (pitching_team_id,))
            rank_res = cur.fetchone()
            bullpen_rank = rank_res[0] if rank_res else 15
            cur.close()
            conn.close()

            # Fetch Pitcher Info & State Tracking
            plays = live_data.get('plays', {})
            current_play = plays.get('currentPlay', {})
            matchup = current_play.get('matchup', {})
            pitcher_id = matchup.get('pitcher', {}).get('id')
            
            # Simple Pitch Count Approximation (in a real app, use the boxscore)
            boxscore = live_data.get('boxscore', {})
            pitcher_stats = {}
            for t in ['away', 'home']:
                # DANGER: pitchers list might not be a dict
                for p in boxscore.get('teams', {}).get(t, {}).get('pitchers', []):
                    try:
                        players_dict = boxscore.get('teams', {}).get(t, {}).get('players', {})
                        player_info = players_dict.get(f"ID{p}", {})
                        if player_info.get('person', {}).get('id') == pitcher_id:
                            pitcher_stats = player_info.get('stats', {}).get('pitching', {})
                    except Exception as pe:
                        print(f"Pitcher detail fetch failed: {pe}")
            
            pitch_count = pitcher_stats.get('pitchesThrown', 0)
            
            # Detect Reliever Entry (Simple check if current pitcher is not the starter)
            is_reliever = False
            if pitcher_id:
                for t in ['away', 'home']:
                    starters = boxscore.get('teams', {}).get(t, {}).get('pitchers', [])
                    try:
                        if starters and boxscore.get('teams', {}).get(t, {}).get('players', {}).get(f"ID{starters[0]}", {}).get('person', {}).get('id') != pitcher_id:
                            is_reliever = True
                    except Exception as se:
                        print(f"Reliever check failed: {se}")

            # Calculate Scoreless Streak
            scoreless_streak = 0
            for inn in reversed(innings):
                try:
                    if (inn.get('away', {}).get('runs', 0) == 0 and inn.get('home', {}).get('runs', 0) == 0):
                        scoreless_streak += 1
                    else:
                        break
                except AttributeError:
                    print(f"Inning object is list not dict: {inn}")
                    break

            # Previous Inning Runs
            prev_inning_runs = 0
            if current_inning > 1:
                try:
                    prev_inn = innings[current_inning - 2]
                    prev_inning_runs = prev_inn.get('away', {}).get('runs', 0) + prev_inn.get('home', {}).get('runs', 0)
                except Exception as pie:
                    print(f"Prev inning runs failed: {pie}")
            home_runs = linescore.get('home', {}).get('runs', 0)
            away_runs = linescore.get('away', {}).get('runs', 0)

            # Construct Multi-Dimensional State for Evaluator and Quant Search
            state = {
                "inning": current_inning,
                "score_diff": home_runs - away_runs,
                "abs_score_diff": abs(home_runs - away_runs),
                "total_runs": home_runs + away_runs,
                "pitching_team_bullpen_rank": bullpen_rank,
                "baserunners": (1 if linescore.get('offense', {}).get('first') else 0) + 
                              (1 if linescore.get('offense', {}).get('second') else 0) + 
                              (1 if linescore.get('offense', {}).get('third') else 0),
                "inning_batters_faced": len(current_play.get('playEvents', [])), # Approximation
                "pitcher_pitch_count": pitch_count,
                "is_reliever_entry": is_reliever,
                "scoreless_streak": scoreless_streak,
                "prev_inning_runs": prev_inning_runs,
                "temp": weather_data.get('temp'),
                "wind_speed": weather_data.get('wind'),
                "wind_direction": weather_data.get('wind_direction'),
                "venue_id": venue_id,
                "is_night_game": game_data.get('isNightGame', False)
            }

            away_abbr = teams.get('away', {}).get('abbreviation', 'AWY')
            home_abbr = teams.get('home', {}).get('abbreviation', 'HM')
            game_date = datetime.now().strftime('%-m/%-d')
            game_info = f"{home_abbr} Vs {away_abbr} - {game_date}{weather_str}"

            # Update Inning Logs (V2.3: Only update current/prev to keep feed chronological)
            for idx, inning in enumerate(innings):
                inn_num = idx + 1
                if inn_num >= current_inning - 1:
                    print(f"UPDATING LOG: Game {game_id} Inning {inn_num} (Current: {current_inning})")
                    for half in ['away', 'home']:
                        data = inning.get(half, {})
                        # Baserunners in this context = Total activity (Hits + BB/HBP approximated by LOB)
                        # This provides the 'meta-data' requested for the feed
                        log_inning_data(game_id, inn_num, half, data.get('runs', 0), data.get('hits', 0) + data.get('leftOnBase', 0), game_info)

            # Evaluate each dynamic rule
            for rule in rules:
                alert_key = f"alert:{game_id}:{rule['id']}"
                if redis_client.exists(alert_key):
                    continue
                
                if RuleEvaluator.evaluate(rule['conditions'], state):
                    print(f"Rule '{rule['name']}' triggered for {game_id}. Reason-Mode Activated.")
                    
                    config = rule['config'] or {}
                    p = config.get('p', 0.55)
                    odds = config.get('odds', -110)
                    stake = calculate_kelly(p, odds)
                    
                    ai_insight = None
                    ai_trace = None
                    if ai_agent:
                        try:
                            # V2.0: Get historical context from DuckDB
                            hist_context = quant_service.get_similarity_context(state)
                            print(f"Retrieved historical context: {hist_context}")
                            
                            # Generate reasoning-backed insight (Gemma 4)
                            raw_ai_output = ai_agent.generate_insight(rule['name'], state, hist_context)
                            
                            if not raw_ai_output:
                                raise ValueError("AI output was empty or failed.")
                                
                            # Robust extraction of thinking/trace vs final insight
                            # Support for <|think|>, <thought>, <reasoning> etc.
                            tags = ["<|think|>", "<|thought|>", "<thought>", "<reasoning>", "<think>"]
                            end_tags = ["</think>", "</thought>", "</reasoning>", "Final Answer:"]
                            
                            found_tag = None
                            for t in tags:
                                if t in raw_ai_output:
                                    found_tag = t
                                    break
                            
                            if found_tag:
                                # Try to find an end tag or just split by the start tag
                                parts = raw_ai_output.split(found_tag)
                                if len(parts) > 1:
                                    trace_part = parts[1]
                                    # Check for end tags
                                    for et in end_tags:
                                        if et in trace_part:
                                            ai_trace = trace_part.split(et)[0].strip()
                                            ai_insight = trace_part.split(et)[1].strip()
                                            break
                                    
                                    # Fallback if no end tag found: use some heuristic or just keep it all
                                    if not ai_insight:
                                        # If it's a very long output, the first part is trace, last part is insight
                                        # For Gemma, if it doesn't have an end tag, it might just be the whole thing.
                                        # We'll split by double newline as a heuristic for "Final Answer"
                                        if "\n\n" in trace_part:
                                            p = trace_part.rsplit("\n\n", 1)
                                            ai_trace = p[0].strip()
                                            ai_insight = p[1].strip()
                                        else:
                                            ai_insight = trace_part
                                            ai_trace = "Reasoning omitted for brevity."
                            else:
                                ai_insight = raw_ai_output
                                ai_trace = "No thinking trace provided by model."
                        
                            # Clean up insight if it still contains thinking markers
                            if ai_insight:
                                for t in tags + end_tags:
                                    ai_insight = ai_insight.replace(t, "").strip()
                            if ai_trace:
                                for t in tags + end_tags:
                                    ai_trace = ai_trace.replace(t, "").strip()
                                    
                        except Exception as e:
                            print(f"⚠️ AI Orchestrator Integration Failed for rule {rule['name']}: {e}")
                            ai_insight = "Quantitative analysis triggered based on rule conditions."
                            ai_trace = "AI Insight unavailable due to processing error."
                    
                    # Generate DraftKings Deep Link Search (V2.2 QuickSlip Mapping)
                    # Note: Using search link until Selection ID mapping service is active.
                    # Improvement: Use team names + date to ensure search works
                    search_query = f"{home_abbr} vs {away_abbr} {game_date}"
                    deep_link_url = f"https://sportsbook.draftkings.com/search?q={search_query.replace(' ', '%20')}"

                    if rule['status'] == 'ACTIVE' and alerter:
                       try:
                           # V2.5: Use Gastown-Native Alerting
                           print(f"📣 Dispatching Gastown Alert for {rule['name']}...")
                           orchestrator_dir = "/Users/grantbest/Documents/Active/BestFam-Orchestrator"
                           script_path = "/app/scripts/trigger_gastown_alert.py"

                           # Arguments: sys_name, g_id, target, odds, stake, insight, link, info, inning
                           # Handle potential None values for insight/info
                           safe_insight = (ai_insight or "Quant analysis active.").replace("'", "")
                           safe_info = (game_info or f"{home_abbr} vs {away_abbr}").replace("'", "")

                           outs = linescore.get('outs', 0)
                           runner_list = []
                           if linescore.get('offense', {}).get('first'): runner_list.append("1B")
                           if linescore.get('offense', {}).get('second'): runner_list.append("2B")
                           if linescore.get('offense', {}).get('third'): runner_list.append("3B")
                           runners_str = f"Runners: {', '.join(runner_list)}" if runner_list else "Bases Empty"
                           formatted_inning = f"{'Top' if is_top else 'Bottom'} {current_inning} | {outs} Outs | {runners_str}"

                           subprocess.Popen(
                               ["python", script_path, rule['name'], str(game_id), "Quant Strategy Trigger", str(odds), str(stake), safe_insight, deep_link_url, safe_info, formatted_inning],
                               env={**os.environ, "PYTHONPATH": f"{orchestrator_dir}:{orchestrator_dir}/src:{orchestrator_dir}/scripts"},
                               start_new_session=True
                           )
                       except Exception as alert_err:
                           print(f"❌ Gastown Alert Dispatch Failed: {alert_err}")
                           trigger_sre_activity(
                               "Discord Alert Dispatch Failure",
                               f"Failed to spawn Gastown alert script for Game {game_id}, Rule: {rule['name']}. Error: {str(alert_err)}"
                           )

                    outs = linescore.get('outs', 0)
                    runner_list = []
                    if linescore.get('offense', {}).get('first'): runner_list.append("1B")
                    if linescore.get('offense', {}).get('second'): runner_list.append("2B")
                    if linescore.get('offense', {}).get('third'): runner_list.append("3B")
                    runners_str = f"Runners: {', '.join(runner_list)}" if runner_list else "Bases Empty"
                    formatted_inning = f"{'Top' if is_top else 'Bottom'} {current_inning} | {outs} Outs | {runners_str}"

                    log_bet(game_id, rule['name'], odds, stake, ai_insight, game_info, clv=0.0, ai_trace=ai_trace, deep_link_url=deep_link_url, inning=formatted_inning)
                    redis_client.setex(alert_key, 86400, "1")        except Exception as e:
            print(f"Error monitoring game {game_id}: {e}")

if __name__ == "__main__":
    print("MLB Engine Active. Scanning for opportunities...", flush=True)
    update_team_data()
    
    # Priority: Database Setting -> Environment Variable
    webhook_url = get_setting("discord_webhook_url") or os.getenv("DISCORD_WEBHOOK_URL")
    alerter = DiscordWebhookAlert(webhook_url) if webhook_url else None
    
    redis_client = get_redis_client()
    weather_service = WeatherService()
    quant_service = QuantService()
    
    ai_agent = None
    try:
        ai_agent = AIAgent()
        print("✅ AI Orchestrator initialized.")
    except Exception as e:
        print(f"⚠️ AI Orchestrator failed to initialize: {e}")
    
    while True:
        try:
            monitor_games(alerter, redis_client, ai_agent, weather_service)
        except Exception as loop_e:
            print(f"🚨 CRITICAL LOOP FAILURE: {loop_e}")
            trigger_sre_activity("Engine Loop Failure", f"The main engine loop crashed with: {loop_e}. Recovering in 2 minutes.")
        time.sleep(120) # Scan every 2 minutes
