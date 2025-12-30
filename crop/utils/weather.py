
import requests

OPENWEATHER_API_KEY = "0747da042e4d3b43e650286a06b23128"

def fetch_weather(lat, lon):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
    )

    data = requests.get(url).json()

    return {
        "temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "rain": data.get("rain", {}).get("1h", 0),
        "wind": data["wind"]["speed"]
    }
