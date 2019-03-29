import requests
import json
from datetime import datetime
from itertools import groupby
from sensitive import OWM_TOKEN

def api_call(sub_url):
    r = requests.get("https://api.openweathermap.org/data" + sub_url + "&appid=" + OWM_TOKEN)
    data = json.loads(r.text)
    return data

def get_weather_from_home():
    return api_call("/2.5/weather?q=Bretten,DE&units=metric&lang=de")

def get_weather_forecast_from_home():
    return get_weather_forecast_from_location("Bretten,DE")

def get_weather_from_location_name(location):
    return api_call("/2.5/weather?q=" + location + "&units=metric&lang=de")

def get_weather_forecast_from_location(location):
    data = api_call("/2.5/forecast?q=" + location + "&units=metric&lang=de")
    forecasts = data["list"]
    forecast = {}
    for idx, i in enumerate(forecasts):
        forecasts[idx]["dt"] = datetime.fromtimestamp(i["dt"])
        forecasts[idx]["date"] = i["dt"].date()
    for i in forecasts:
        try:
            forecast[i["date"]].append(i)
        except:
            forecast[i["date"]] = [i]
    for i in forecast:
        temp = [i["main"]["temp"] for i in forecast[i]]
        forecast[i] = {
            "temp": sum(temp)/len(temp),
            "temp_min": min(temp),
            "temp_max": max(temp),
            "weather": list(set([i["weather"][0]["description"] for i in forecast[i]]))
        }
    return [data["city"]["name"], forecast]

    
    
