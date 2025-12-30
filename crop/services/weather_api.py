import os
import requests

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(lat, lon):
    if not OPENWEATHER_API_KEY:
        raise Exception("Missing OPENWEATHER_API_KEY in environment variables")

    url = (
        "https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Weather API error: {response.status_code} - {response.text}")

    r = response.json()

    rain = r.get("rain", {}).get("1h") or r.get("rain", {}).get("3h") or 0

    return {
        "temp": r["main"]["temp"],
        "humidity": r["main"]["humidity"],
        "wind": r.get("wind", {}).get("speed", 0),
        "rain": rain
    }
import random

def fetch_weather(lat, lon):
    return {
        "temperature": round(random.uniform(22, 35), 1),
        "humidity": round(random.uniform(40, 80), 1),
        "rainfall": round(random.uniform(0, 10), 1),
        "wind": round(random.uniform(1, 5), 1),
    }
