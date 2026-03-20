import os
import json
import httpx
import ollama


class AIAgent:
    """
    Orchestrates interactions with AI models.
    Priority: Gemini (1st), OpenAI (2nd), Ollama (3rd).
    Claude is only used if explicitly requested in config.
    """

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Ollama (Fallback)
        self.ollama_url = os.getenv(
            "OLLAMA_BASE_URL", "http://host.docker.internal:11434"
        )
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
        self.ollama_client = ollama.Client(host=self.ollama_url)

        self.system_prompt = (
            "You are an expert MLB Quantitative Analyst and Betting Strategist. "
            "You analyze baseball statistics, game state (innings, score, baserunners), "
            "and mathematical models to provide sharp, concise, and highly analytical insights. "
            "Do not use conversational filler. Be direct and confident."
        )

    def generate_insight(self, rule_name: str, game_state: dict) -> str:
        """
        Generates a concise justification for a bet.
        Priority: Gemini -> OpenAI -> Ollama.
        """
        prompt = (
            f"A betting opportunity has been identified based on the '{rule_name}' system.\n\n"
            f"Current Game State Data:\n{json.dumps(game_state, indent=2)}\n\n"
            f"Task: Provide a 1-to-2 sentence analytical justification for why this is a strong bet right now. "
            f"Focus on the data provided. Do not include disclaimers."
        )

        # 1. Gemini (First Priority)
        if self.gemini_key:
            try:
                # Use Gemini 1.5 Flash (free tier)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [
                        {"parts": [{"text": f"{self.system_prompt}\n\n{prompt}"}]}
                    ]
                }
                with httpx.Client() as client:
                    resp = client.post(url, json=payload, timeout=5.0)
                    resp.raise_for_status()
                    return resp.json()["candidates"][0]["content"]["parts"][0][
                        "text"
                    ].strip()
            except Exception as e:
                print(f"Gemini Insight Failed: {e}. Trying OpenAI...")

        # 2. OpenAI (Second Priority)
        if self.openai_key:
            try:
                with httpx.Client() as client:
                    resp = client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.openai_key}"},
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": self.system_prompt},
                                {"role": "user", "content": prompt},
                            ],
                            "max_tokens": 150,
                        },
                        timeout=5.0,
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"OpenAI Insight Failed: {e}. Falling back to Ollama.")

        # 3. Ollama (Final Fallback)
        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            return response["message"]["content"].strip()
        except Exception as e:
            print(f"Ollama Insight Failed: {e}")
            return "AI insight currently unavailable."
