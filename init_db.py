import psycopg2
import os
import time
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta

DEFAULT_RULES = [
    {
        "name": "NR2I Regression",
        "description": "Both teams score in 1st; Game Total <= 9 -> Target: No Run 2nd Inning",
        "status": "ACTIVE",
        "conditions_json": {
            "logic": "AND",
            "conditions": [
                {"attribute": "inning", "operator": "==", "value": 2},
                {"attribute": "runs_scored_half", "operator": "==", "value": 0}
            ]
        }
    },
    {
        "name": "Big Inning Momentum",
        "description": "Previous inning had 3+ runs and 4+ baserunners -> Target: Yes Run Next Inning",
        "status": "ACTIVE",
        "conditions_json": {
            "logic": "AND",
            "conditions": [
                {"attribute": "runs_scored_half", "operator": ">=", "value": 3},
                {"attribute": "baserunners", "operator": ">=", "value": 4}
            ]
        }
    },
    {
        "name": "5th Inning Fatigue",
        "description": "Game Total >= 9; Starter facing lineup 3rd time -> Target: Yes Run 5th Inning",
        "status": "ACTIVE",
        "conditions_json": {
            "logic": "AND",
            "conditions": [
                {"attribute": "inning", "operator": "==", "value": 5},
                {"attribute": "score_diff", "operator": ">=", "value": 0}
            ]
        }
    },
    {
        "name": "Late Bullpen",
        "description": "Game within 3 runs; Both bullpens top-20 ERA -> Target: No Run 8th Inning",
        "status": "ACTIVE",
        "conditions_json": {
            "logic": "AND",
            "conditions": [
                {"attribute": "inning", "operator": "==", "value": 8},
                {"attribute": "pitching_team_bullpen_rank", "operator": "<=", "value": 20}
            ]
        }
    }
]

def init_database():
    """
    Reads the schema.sql file and applies it to the specified database.
    Supports individual env vars or DATABASE_URL.
    """
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        result = urlparse(db_url)
        db_user = result.username
        db_pass = result.password
        db_host = result.hostname
        db_port = result.port or 5432
        db_name = result.path.lstrip('/')
    else:
        db_name = os.getenv("DB_NAME", "mlb_engine")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_user = os.getenv("DB_USER", "admin")
        db_pass = os.getenv("DB_PASS", "password123")

    print(f"Connecting to database {db_name} on {db_host}:{db_port}...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            # Connect to default postgres to create our target DB if it doesn't exist
            conn = psycopg2.connect(
                host=db_host,
                database="postgres",
                user=db_user,
                password=db_pass,
                port=db_port
            )
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {db_name}")
                print(f"Created database {db_name}")
            cur.close()
            conn.close()

            # Connect to the target DB and apply schema
            if db_url:
                conn = psycopg2.connect(db_url)
            else:
                conn = psycopg2.connect(
                    host=db_host,
                    database=db_name,
                    user=db_user,
                    password=db_pass,
                    port=db_port
                )
            cur = conn.cursor()
            
            with open('schema.sql', 'r') as f:
                schema_sql = f.read()
                
            cur.execute(schema_sql)
            conn.commit()
            print(f"✅ Database {db_name} initialized successfully with schema.sql")
            
            # Check if rules exist, if not seed them (Only in Development)
            app_env = os.getenv("APP_ENV", "development")
            cur.execute("SELECT COUNT(*) FROM betting_rules")
            if cur.fetchone()[0] == 0 and app_env == "development":
                print(f"Seeding demo rules for {app_env} environment...")
                for rule in DEFAULT_RULES:
                    cur.execute(
                        "INSERT INTO betting_rules (name, description, status, conditions_json) VALUES (%s, %s, %s, %s)",
                        (rule['name'], rule['description'], rule['status'], json.dumps(rule['conditions_json']))
                    )
                
                # Also seed some demo history if in development
                print("Seeding demo history (Inning Logs & Bet History)...")
                
                # Demo Teams
                teams_data = [
                    (110, 'BAL', 5), (114, 'CLE', 1), (119, 'LAD', 3), (136, 'SEA', 2)
                ]
                for team_id, abbr, rank in teams_data:
                    cur.execute(
                        "INSERT INTO teams (team_id, abbreviation, bullpen_era_rank) VALUES (%s, %s, %s) ON CONFLICT (team_id) DO NOTHING",
                        (team_id, abbr, rank)
                    )

                # Demo Logs
                logs = [
                    (744880, 1, 'top', 1, 2, "BAL Vs NYY - 3/13"),
                    (744880, 1, 'bottom', 2, 3, "BAL Vs NYY - 3/13"),
                    (745201, 4, 'bottom', 0, 4, "LAD Vs SF - 3/13")
                ]
                for g_id, inn, half, runs, runners, info in logs:
                    cur.execute(
                        "INSERT INTO inning_logs (game_id, inning_number, half, runs_scored, baserunners, game_info) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                        (g_id, inn, half, runs, runners, info)
                    )

                # Demo History
                history = [
                    (744880, 'NR2I Regression', -115, 0.05, 'WON', "Low scoring environment with elite bullpen relief.", datetime.now() - timedelta(hours=2)),
                    (746174, 'Big Inning Momentum', 105, 0.06, 'WON', "Momentum carried into the next frame as predicted.", datetime.now() - timedelta(hours=3)),
                    (745201, '5th Inning Fatigue', -110, 0.03, 'PENDING', "Starter pitch count exceeds 85; 3rd time through order.", datetime.now() - timedelta(minutes=5))
                ]
                for g_id, sys, odds, stake, res, ai, dt in history:
                    cur.execute(
                        "INSERT INTO bet_tracking (game_id, system_triggered, odds_taken, stake, result, ai_insight, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (g_id, sys, odds, stake, res, ai, dt)
                    )

                conn.commit()
                print(f"✅ Seeded demo data for {app_env} environment.")
            else:
                print(f"Skipping demo data seeding for {app_env} environment (or rules already exist).")

            cur.close()
            conn.close()
            break
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2)
            else:
                print(f"❌ Failed to initialize database {db_name} after {max_retries} attempts.")

if __name__ == "__main__":
    init_database()
