import requests
from config import CITY_LAT, CITY_LON

def get_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={CITY_LAT}&longitude={CITY_LON}&current_weather=true"
        response = requests.get(url, timeout=10)
        data = response.json()
        temp = data["current_weather"]["temperature"]
        return f"Сейчас в Костроме: {temp}°C. Надевай трусы потеплее!"
    except Exception as e:
        return "Не удалось получить погоду. Смотри в окно, сучка!"
