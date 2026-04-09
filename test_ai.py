import os
import json
from ai_orchestrator import AIAgent
from dotenv import load_dotenv

load_dotenv()

agent = AIAgent()
agent.ollama_model = "gemma4:latest"
state = {
    "inning": 3,
    "score_diff": 0,
    "pitching_team_bullpen_rank": 15,
    "temp": 72,
    "wind_speed": 5
}
context = {
    "historical_win_prob": 0.52,
    "sample_size": 1200,
    "avg_total_runs": 8.5
}

print("Generating insight for '3rd Inning Pivot'...")
res = agent.generate_insight("3rd Inning Pivot", state, context)
print(f"RAW OUTPUT:\n{res}")

print("\n" + "="*50 + "\n")

state["inning"] = 5
print("Generating insight for '5th Inning Fatigue'...")
res2 = agent.generate_insight("5th Inning Fatigue", state, context)
print(f"RAW OUTPUT:\n{res2}")
