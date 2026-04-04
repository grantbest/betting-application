import os
import json
import httpx
import ollama
from typing import Optional, Dict, Any

class AIAgent:
    """
    Orchestrates interactions with AI models for MLB Quant Analysis.
    Lynchpin: Gemma 4 (Local via Ollama) with Thinking Mode.
    Fallback: Gemini 1.5 Flash -> OpenAI GPT-4o-mini.
    """
    def __init__(self):
        # Ollama (Primary for Gemma 4)
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "gemma4:26b")
        self.ollama_client = ollama.Client(host=self.ollama_url)
        
        # Cloud API Keys
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        
        self.system_prompt = (
            "<|think|> You are an expert MLB Quantitative Analyst. "
            "Use your internal reasoning process to analyze the provided live game state "
            "and historical context. Focus on identifying 'Edge'—where the model probability "
            "differs from the implied bookmaker odds. "
            "Provide a concise final justification. Do not use conversational filler."
        )

    def generate_insight(self, rule_name: str, game_state: dict, historical_context: Optional[dict] = None) -> str:
        """
        Generates a reasoning-backed justification for a bet.
        If Gemma 4 is used, it utilizes the native thinking mode.
        """
        context_str = ""
        if historical_context:
            context_str = f"\n\nHistorical Context (DuckDB):\n{json.dumps(historical_context, indent=2)}"

        prompt = (
            f"Rule Triggered: '{rule_name}'\n"
            f"Live Game State:\n{json.dumps(game_state, indent=2)}"
            f"{context_str}\n\n"
            "Task: Reason about the value of this bet. Compare the situation to historical norms. "
            "Provide a 2-sentence analytical conclusion."
        )

        # 1. Gemma 4 (Local Lynchpin)
        try:
            response = self.ollama_client.chat(model=self.ollama_model, messages=[
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': prompt}
            ])
            content = response['message']['content'].strip()
            # In V2.0, we keep the raw output including thinking tags for the audit log
            return content
        except Exception as e:
            print(f"Gemma 4 (Local) Failed: {e}. Falling back to Cloud...")

        # 2. Gemini (First Cloud Fallback)
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": f"{self.system_prompt}\n\n{prompt}"}]}]
                }
                with httpx.Client() as client:
                    resp = client.post(url, json=payload, timeout=8.0)
                    resp.raise_for_status()
                    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                print(f"Gemini Insight Failed: {e}. Trying OpenAI...")

        # 3. OpenAI (Final Fallback)
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
                                {"role": "user", "content": prompt}
                            ],
                            "max_tokens": 200
                        },
                        timeout=8.0
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"OpenAI Insight Failed: {e}")
                return "AI insight currently unavailable."
