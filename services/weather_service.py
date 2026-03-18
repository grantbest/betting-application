
import requests

API_KEY = "your_real_weather_api_key"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

class WeatherService:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key

    def get_current_weather(self, location):
        params = {
            'key': self.api_key,
            'q': location,
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()
        weather_info = {
            'temperature': weather_data['current']['temp_c'],
            'condition': weather_data['current']['condition']['text'],
            'wind_speed': weather_data['current']['wind_kph'],
            'precipitation': weather_data['current']['precip_mm'],
        }
        return weather_info
