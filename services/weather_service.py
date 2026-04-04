import statsapi as mlb
import re

class WeatherService:
    """
    Service to fetch real-time weather data from the MLB Stats API.
    """
    def __init__(self, api_key=None, base_url=None):
        # API Key is currently not needed as we use MLB Stats API
        self.api_key = api_key
        self.base_url = base_url

    def get_weather_data(self, game_id):
        """Fetches weather directly from the MLB game object."""
        try:
            game = mlb.get('game', {'gamePk': game_id})
            boxscore_info = game.get('liveData', {}).get('boxscore', {}).get('info', [])
            
            temp = None
            wind = None
            wind_direction = "Calm"
            conditions = "Clear"

            for entry in boxscore_info:
                label = entry.get('label')
                value = entry.get('value')
                
                if label == 'Weather':
                    # Value format: '69 degrees, Partly Cloudy.'
                    temp_match = re.search(r'(\d+) degrees', value)
                    if temp_match:
                        temp = int(temp_match.group(1))
                    
                    cond_match = re.search(r'degrees, (.*)\.', value)
                    if cond_match:
                        conditions = cond_match.group(1).strip()
                
                elif label == 'Wind':
                    # Value format: '15 mph, L To R.' or '15 mph, Out To CF.'
                    wind_match = re.search(r'(\d+) mph', value)
                    if wind_match:
                        wind = int(wind_match.group(1))
                    
                    dir_match = re.search(r'mph, (.*)\.', value)
                    if dir_match:
                        wind_direction = dir_match.group(1).strip()

            return {
                "temp": temp or 72,
                "wind": wind or 5,
                "wind_direction": wind_direction,
                "conditions": conditions,
                "status": "real-time" if temp else "default"
            }
        except Exception as e:
            print(f"Error fetching weather from MLB API: {e}")
            return {"status": "error", "temp": 72, "wind": 5, "conditions": "Clear"}

    def annotate_events_with_weather(self, events):
        # Legacy support if needed
        return events
