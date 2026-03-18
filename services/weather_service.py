import requests
from datetime import datetime

class WeatherService:
    """
    Service to fetch real-time weather data and annotate events.
    """
    def __init__(self, api_key=None, base_url="http://api.weatherprovider.com"):
        self.api_key = api_key
        self.base_url = base_url

    def get_weather_data(self, location):
        # Simulated or real API call
        # In a real environment, this would hit OpenWeatherMap or similar
        try:
            response = requests.get(f"{self.base_url}/weather", params={
                'q': location,
                'appid': self.api_key
            }, timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"status": "limited", "temp": 72, "wind": 5} # Fallback
        except Exception:
            return {"status": "limited", "temp": 72, "wind": 5} # Fallback

    def annotate_events_with_weather(self, events):
        annotated_events = []
        for event in events:
            location = event.get('location', 'Unknown')
            weather = self.get_weather_data(location)
            event['weather'] = weather
            annotated_events.append(event)
        return annotated_events
