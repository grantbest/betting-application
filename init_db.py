import psycopg2
import os
import time
from urllib.parse import urlparse

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
