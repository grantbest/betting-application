import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "mlb_engine"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "SecureManagedPass2026!")
    )

def apply_migration():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE bet_tracking ADD COLUMN IF NOT EXISTS inning VARCHAR(20);")
        conn.commit()
        print("✅ Added 'inning' column to 'bet_tracking' table.")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    apply_migration()
