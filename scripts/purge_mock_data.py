import psycopg2
import os
import sys

# Database connection configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "mlb_engine")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")
DB_PORT = os.getenv("DB_PORT", "5432")
APP_ENV = os.getenv("APP_ENV", "development")

MOCK_GAME_IDS = [744798, 744880, 745201, 745282, 745686, 745846, 745932, 746174, 746416, 746496, 746577, 746820, 746901, 747061, 747147]

def purge_mock_data():
    if APP_ENV != "production":
        print(f"Current environment is {APP_ENV}. This script is intended for PRODUCTION cleanup.")
        confirm = input("Are you sure you want to proceed? (y/N): ")
        if confirm.lower() != 'y':
            return

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

        print(f"Purging mock data from {DB_NAME}...")
        
        # Purge logs and bets associated with mock game IDs
        cur.execute("DELETE FROM inning_logs WHERE game_id = ANY(%s)", (MOCK_GAME_IDS,))
        logs_deleted = cur.rowcount
        
        cur.execute("DELETE FROM bet_tracking WHERE game_id = ANY(%s)", (MOCK_GAME_IDS,))
        bets_deleted = cur.rowcount
        
        conn.commit()
        print(f"✅ Purged {logs_deleted} mock inning logs and {bets_deleted} mock bets.")

    except Exception as e:
        print(f"❌ Error purging mock data: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    purge_mock_data()
