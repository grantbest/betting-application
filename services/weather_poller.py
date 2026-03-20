import time
import requests
from cachetools import TTLCache
from threading import Thread

# Caching layer, using time-to-live cache for 30 minutes expiration
cache = TTLCache(maxsize=100, ttl=1800)


class WeatherPoller(Thread):
    def __init__(self, api_key, venues, poll_interval=900):
        super().__init__()
        self.api_key = api_key
        self.venues = venues
        self.poll_interval = poll_interval
        self.api_url = "http://api.weatherstack.com/current"

    def run(self):
        while True:
            for venue in self.venues:
                if venue not in cache:
                    try:
                        response = requests.get(
                            self.api_url,
                            params={"access_key": self.api_key, "query": venue},
                        )
                        if response.status_code == 200:
                            weather_data = response.json()
                            cache[venue] = weather_data
                            print(f"Updated weather data for {venue}")
                        else:
                            print(
                                f"Failed to get data for {venue}: {response.status_code}"
                            )
                    except Exception as e:
                        print(
                            f"Exception occurred while fetching data for {venue}: {e}"
                        )
                else:
                    print(f"Using cached data for {venue}")
            time.sleep(self.poll_interval)


# Example Usage
api_key = "your_api_key"
venues = ["New York", "Los Angeles", "Chicago"]
weather_poller = WeatherPoller(api_key, venues)
weather_poller.start()
