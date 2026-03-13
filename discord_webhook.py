import requests
import json

class DiscordWebhookAlert:
    """
    A class to send formatted alerts to a Discord webhook.
    """

    def __init__(self, webhook_url: str):
        if not webhook_url:
            raise ValueError("Discord webhook URL cannot be empty.")
        self.webhook_url = webhook_url

    def send_alert(self, system_name: str, game_id: int, bet_target: str, odds: int, stake_percentage: float, ai_insight: str = None):
        """
        Formats and sends a betting alert to the Discord webhook, optionally including an AI-generated insight.
        """
        embed = {
            "title": f"📈 {system_name} Opportunity",
            "description": f"A high-probability betting opportunity has been identified for Game ID **{game_id}**.\n\n" + (f"🤖 **AI Analyst Insight:**\n*{ai_insight}*" if ai_insight else ""),
            "color": 3447003,  # Blue
            "fields": [
                {
                    "name": "Game ID",
                    "value": str(game_id),
                    "inline": True
                },
                {
                    "name": "Bet",
                    "value": bet_target,
                    "inline": True
                },
                {
                    "name": "Odds",
                    "value": str(odds),
                    "inline": True
                },
                {
                    "name": "Recommended Stake",
                    "value": f"**{stake_percentage:.2%}** of Bankroll",
                    "inline": True
                }
            ],
            "footer": {
                "text": "WE do it inc. | Please Bet Responsibly"
            }
        }

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"Successfully sent alert for Game ID: {game_id}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending Discord alert: {e}")