import psycopg2
import os
import sys
import random
from datetime import datetime, timedelta

# Database connection configuration (defaulting to local dev)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "mlb_engine")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")
DB_PORT = os.getenv("DB_PORT", "5432")

def seed_data(teams_only=False):
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        cur = conn.cursor()

        print(f"Clearing existing data in {DB_NAME}...")
        cur.execute("TRUNCATE TABLE bet_tracking, inning_logs, teams, betting_rules RESTART IDENTITY CASCADE;")

        # 1. Seed Teams & Bullpen Rankings
        print("Seeding Teams & Bullpen Rankings...")
        teams_data = [
            (108, 'LAA', 28), (109, 'AZ', 25), (110, 'BAL', 5), (111, 'BOS', 12),
            (112, 'CHC', 15), (113, 'CIN', 18), (114, 'CLE', 1), (115, 'COL', 30),
            (116, 'DET', 10), (117, 'HOU', 4), (118, 'KC', 22), (119, 'LAD', 3),
            (120, 'WSH', 26), (121, 'NYM', 8), (133, 'OAK', 29), (134, 'PIT', 14),
            (135, 'SD', 7), (136, 'SEA', 2), (137, 'SF', 16), (138, 'STL', 13),
            (139, 'TB', 11), (140, 'TEX', 17), (141, 'TOR', 20), (142, 'MIN', 9),
            (143, 'PHI', 6), (144, 'ATL', 19), (145, 'CWS', 27), (146, 'MIA', 24),
            (147, 'NYY', 21), (158, 'MIL', 23)
        ]
        cur.executemany("INSERT INTO teams (team_id, abbreviation, bullpen_era_rank) VALUES (%s, %s, %s)", teams_data)

        # 2. Seed Betting Rules
        print("Seeding Betting Rules Engine...")
        rules = [
            ('NR2I Regression', 'Both teams score in 1st; Game Total <= 9 -> Target: No Run 2nd Inning', 'ACTIVE', '{"total_limit": 9, "first_inning_runs": "both"}'),
            ('Big Inning Momentum', 'Previous inning had 3+ runs and 4+ baserunners -> Target: Yes Run Next Inning', 'ACTIVE', '{"min_runs": 3, "min_baserunners": 4}'),
            ('5th Inning Fatigue', 'Game Total >= 9; Starter facing lineup 3rd time -> Target: Yes Run 5th Inning', 'ACTIVE', '{"total_limit": 9, "min_batters": 18}'),
            ('Late Bullpen', 'Game within 3 runs; Both bullpens top-20 ERA -> Target: No Run 8th Inning', 'ACTIVE', '{"max_diff": 3, "max_bullpen_rank": 20}')
        ]
        cur.executemany("INSERT INTO betting_rules (name, description, status, conditions_json) VALUES (%s, %s, %s, %s)", rules)

        if not teams_only:
            # 3. Seed Inning Logs (Simulating raw data feed)
            print("Seeding Live Inning Logs...")
            logs = []
            logs.append((744798, 3, 'top', 3, 5, 9))
            logs.append((744880, 1, 'top', 1, 2, 6))
            logs.append((744880, 1, 'bottom', 2, 3, 7))
            logs.append((745201, 4, 'bottom', 0, 4, 10))
            cur.executemany("INSERT INTO inning_logs (game_id, inning_number, half, runs_scored, baserunners, batters_faced_total) VALUES (%s, %s, %s, %s, %s, %s)", logs)

            # 4. Seed Bet History
            print("Seeding Bet History & Analytics...")
            history = [
                (744880, 'NR2I Regression', -115, 0.05, 'WON', "Low scoring environment with elite bullpen relief.", datetime.now() - timedelta(hours=2)),
                (745282, 'NR2I Regression', -110, 0.04, 'LOST', "High velocity offense overcame regression pattern.", datetime.now() - timedelta(hours=5)),
                (745686, 'NR2I Regression', -105, 0.05, 'WON', "Standard regression in favorable park factors.", datetime.now() - timedelta(days=1)),
                (744798, 'Big Inning Momentum', 110, 0.06, 'PENDING', "Offense still hot after 3-run burst.", datetime.now() - timedelta(minutes=15)),
                (746174, 'Big Inning Momentum', 105, 0.06, 'WON', "Momentum carried into the next frame as predicted.", datetime.now() - timedelta(hours=3)),
                (746416, 'Big Inning Momentum', 115, 0.05, 'WON', "Reliever struggled to find zone after long wait.", datetime.now() - timedelta(days=1)),
                (745201, '5th Inning Fatigue', -110, 0.03, 'PENDING', "Starter pitch count exceeds 85; 3rd time through order.", datetime.now() - timedelta(minutes=5)),
                (746577, '5th Inning Fatigue', -120, 0.03, 'LOST', "Starter pulled early; bullpen escaped jam.", datetime.now() - timedelta(hours=8)),
                (746820, 'Late Bullpen', -115, 0.08, 'WON', "Top-5 ERA bullpen secured the clean inning.", datetime.now() - timedelta(hours=1)),
                (746901, 'Late Bullpen', -110, 0.07, 'WON', "Defensive shifts mitigated late scoring threats.", datetime.now() - timedelta(days=2))
            ]
            cur.executemany("INSERT INTO bet_tracking (game_id, system_triggered, odds_taken, stake, result, ai_insight, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", history)

        conn.commit()
        print(f"\n✅ {DB_NAME} seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding database {DB_NAME}: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    teams_only_flag = "--teams-only" in sys.argv
    seed_data(teams_only=teams_only_flag)
