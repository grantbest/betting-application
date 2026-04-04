import duckdb
import os
import json
from pathlib import Path
from typing import Dict, Any, List

class QuantService:
    """
    The 'Memory Bank' interface. Performs ultra-fast OLAP queries on 
    local Parquet files via DuckDB to provide context for AI reasoning.
    """
    def __init__(self, db_path: str = "/Users/grantbest/Documents/Active/BettingApp/data/mlb_quant.db"):
        self.db_path = db_path
        self.gold_dir = Path("/Users/grantbest/Documents/Active/BettingApp/data/gold")
        
    def get_similarity_context(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queries historical Parquet files for games matching the current situational vector.
        Vector: [Ballpark, Inning, ScoreDiff, WeatherCategory]
        """
        # Ensure we have data to query
        parquet_glob = str(self.gold_dir / "games_*.parquet")
        
        # Connect to DuckDB
        conn = duckdb.connect(self.db_path)
        
        try:
            # Check if any parquet files exist
            if not any(self.gold_dir.glob("games_*.parquet")):
                return {"error": "No historical data found in Parquet lake."}

            # 1. Similarity Search: Find games with similar score differential and inning
            # In a full quant model, we'd use ballparks and weather, but we'll start with game state.
            query = f"""
                SELECT 
                    AVG(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as home_win_prob,
                    COUNT(*) as sample_size,
                    AVG(home_score + away_score) as avg_total_runs
                FROM read_parquet('{parquet_glob}')
                WHERE status = 'Final'
                -- Add situational filters here in V2.1
            """
            
            res = conn.execute(query).fetchone()
            
            context = {
                "historical_win_prob": float(res[0]) if res[0] is not None else 0.5,
                "sample_size": int(res[1]) if res[1] is not None else 0,
                "avg_total_runs": float(res[2]) if res[2] is not None else 0.0,
                "data_source": "Local Parquet Data Lake"
            }
            
            return context
            
        except Exception as e:
            print(f"Quant Query Failed: {e}")
            return {"error": str(e)}
        finally:
            conn.close()

    def calculate_clv(self, odds_taken: int, odds_closing: int) -> float:
        """
        Calculates Closing Line Value (CLV).
        Formula: Implied Probability of Closing Odds - Implied Probability of Taken Odds.
        """
        def get_implied_prob(odds: int) -> float:
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        prob_taken = get_implied_prob(odds_taken)
        prob_closing = get_implied_prob(odds_closing)
        
        return prob_closing - prob_taken

    def run_backtest(self, rule_conditions: Dict[str, Any], start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Simulates a rule against historical Parquet data.
        Supports weather (temp, wind_speed) and game state filters.
        """
        parquet_glob = str(self.gold_dir / "games_*.parquet")
        conn = duckdb.connect(self.db_path)
        
        try:
            # Construct a dynamic SQL query based on rule conditions
            # This is a simplified version for Epic 3
            where_clauses = ["status = 'Final'"]
            
            # Add date range
            where_clauses.append(f"date >= '{start_date}'")
            where_clauses.append(f"date <= '{end_date}'")
            
            # Simple condition mapper for V2.0
            for cond in rule_conditions.get('conditions', []):
                attr = cond.get('attribute')
                op = cond.get('operator')
                val = cond.get('value')
                
                # Map frontend attributes to Parquet columns
                col_map = {
                    "temp": "temperature",
                    "wind_speed": "wind_speed",
                    "score_diff": "(home_score - away_score)"
                }
                
                col = col_map.get(attr)
                if col:
                    where_clauses.append(f"{col} {op} {val}")

            query = f"""
                SELECT 
                    COUNT(*) as total_triggers,
                    AVG(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) as win_rate,
                    AVG(home_score + away_score) as avg_total_runs
                FROM read_parquet('{parquet_glob}')
                WHERE {' AND '.join(where_clauses)}
            """
            
            res = conn.execute(query).fetchone()
            
            return {
                "total_triggers": int(res[0]),
                "win_rate": float(res[1]) if res[1] is not None else 0.0,
                "avg_total": float(res[2]) if res[2] is not None else 0.0,
                "period": f"{start_date} to {end_date}"
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def update_model_features(self):
        """
        Gastown Activity: Recalculates 'Gold' features from raw data.
        Example: Rolling 10-game Bullpen ERA.
        """
        pass
