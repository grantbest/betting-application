import os
import json
import ollama

class AIAgent:
    """
    Orchestrates interactions with the local Ollama AI model.
    """
    def __init__(self):
        # Default to host.docker.internal when running in Docker, otherwise localhost
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self.client = ollama.Client(host=self.base_url)
        
        self.system_prompt = (
            "You are an expert MLB Quantitative Analyst and Betting Strategist. "
            "You analyze baseball statistics, game state (innings, score, baserunners), "
            "and mathematical models to provide sharp, concise, and highly analytical insights. "
            "Do not use conversational filler. Be direct and confident."
        )

    def generate_insight(self, rule_name: str, game_state: dict) -> str:
        """
        Generates a concise, natural-language explanation for why a specific betting rule triggered.
        """
        prompt = (
            f"A betting opportunity has been identified based on the '{rule_name}' system.\n\n"
            f"Current Game State Data:\n{json.dumps(game_state, indent=2)}\n\n"
            f"Task: Provide a 1-to-2 sentence analytical justification for why this is a strong bet right now. "
            f"Focus on the data provided (e.g., bullpen rank, runs scored, runners on base). "
            f"Do not include disclaimers or introductory phrases."
        )

        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"AI Insight Generation Failed: {e}")
            return "AI insight currently unavailable due to connection error."

    def analyze_strategy_performance(self, history_data: list, rules_data: list) -> str:
        """
        Analyzes historical betting data against current rules to suggest optimizations.
        """
        prompt = (
            f"Review the following historical betting data and active rules.\n\n"
            f"Active Rules:\n{json.dumps(rules_data, indent=2)}\n\n"
            f"Bet History (sample):\n{json.dumps(history_data, indent=2)}\n\n"
            f"Task: Identify any patterns in the losses. Suggest specific tweaks to the JSON conditions "
            f"of the rules to improve the win rate. Format your response clearly with a 'Findings' section "
            f"and a 'Suggested Tweaks' section."
        )

        try:
            response = self.client.chat(model=self.model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content'].strip()
        except Exception as e:
            print(f"AI Strategy Analysis Failed: {e}")
            return "Strategy analysis failed."
