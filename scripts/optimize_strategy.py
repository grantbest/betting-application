import os
import psycopg2
import sys

# Ensure the parent directory is in the path to import ai_orchestrator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_orchestrator import AIAgent

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "mlb_engine")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password123")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def fetch_data():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT rule_id, name, conditions_json FROM betting_rules WHERE status = 'ACTIVE'")
        rules = [{"id": r[0], "name": r[1], "conditions": r[2]} for r in cur.fetchall()]
        
        cur.execute("SELECT game_id, system_triggered, result FROM bet_tracking WHERE result != 'PENDING' ORDER BY created_at DESC LIMIT 100")
        history = [{"game_id": h[0], "system": h[1], "result": h[2]} for h in cur.fetchall()]
        
        cur.close()
        return rules, history
    except Exception as e:
        print(f"Database error: {e}")
        return [], []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Fetching data for AI Strategy Optimizer...")
    rules, history = fetch_data()
    
    if not rules or not history:
        print("Not enough data to analyze. Ensure you have active rules and completed bets.")
        sys.exit(1)
        
    print(f"Loaded {len(rules)} active rules and {len(history)} historical bets.")
    print("\nConsulting the AI Analyst (Local Ollama)...\n" + "-"*50)
    
    agent = AIAgent()
    analysis = agent.analyze_strategy_performance(history, rules)
    
    print("\n🧠 AI STRATEGY RECOMMENDATIONS:\n")
    print(analysis)
    print("\n" + "-"*50)
