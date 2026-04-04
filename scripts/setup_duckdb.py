import duckdb
import os
from pathlib import Path

# Base Directory for BettingApp Data
DATA_DIR = Path("/Users/grantbest/Documents/Active/BettingApp/data")

def setup_directories():
    """Creates the local folder structure for the Managed Dataset."""
    subdirs = ["raw", "bronze", "gold"]
    for sd in subdirs:
        (DATA_DIR / sd).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created directory structure in {DATA_DIR}")

def initialize_duckdb():
    """Initializes a persistent DuckDB database file."""
    db_path = DATA_DIR / "mlb_quant.db"
    
    # Connect (creates if not exists)
    conn = duckdb.connect(str(db_path))
    
    # Create basic views/tables if needed
    conn.execute("CREATE TABLE IF NOT EXISTS meta_log (event TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("INSERT INTO meta_log (event) VALUES ('Database Initialized v2.0')")
    
    # Close
    conn.close()
    print(f"✅ Initialized persistent DuckDB: {db_path}")

if __name__ == "__main__":
    setup_directories()
    initialize_duckdb()
