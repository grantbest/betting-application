import os
import requests

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.weatherapi.com/v1/current.json"

    def get_weather(self, location: str) -> dict:
        params = {
            'key': self.api_key,
            'q': location,
        }
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        return response.json()

weather_service = WeatherService(api_key=os.getenv('WEATHER_API_KEY'))