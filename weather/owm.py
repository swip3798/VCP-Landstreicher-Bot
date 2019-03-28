import requests
import json
from datetime import datetime
from itertools import groupby
# from sensitive import OWM_TOKEN
OWM_TOKEN = "ccbbefeda55fabefd3dcfa0527cd0d5e"


def api_call(sub_url):
    r = requests.get("https://api.openweathermap.org/data" + sub_url + "&appid=" + OWM_TOKEN)
    data = json.loads(r.text)
    return data

def get_weather_from_home():
    return api_call("/2.5/weather?q=Bretten,DE&units=metric&lang=de")

def get_weather_from_location_name(location):
    return api_call("/2.5/weather?q=" + location + "&units=metric&lang=de")

def get_weather_forecast_from_location(location):
    return api_call("/2.5/forecast?q=" + location + "&units=metric&lang=de")


if __name__ == "__main__":
    data = get_weather_forecast_from_location("Bretten,DE")
    forecasts = data["list"]
    forecast = {}
    for idx, i in enumerate(forecasts):
        forecasts[idx]["dt"] = datetime.fromtimestamp(i["dt"])
        forecasts[idx]["date"] = i["dt"].date()
    for i in forecasts:
        forecast[i["date"]] = i
    dates = list(forecast.keys())
    dates.sort()


    print(dates)
    
    
    
