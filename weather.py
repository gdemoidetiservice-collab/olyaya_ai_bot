import requests
from config import CITY_LAT, CITY_LON, CITY_NAME


def get_weather() -> str:
    """Получает погоду в Костроме через Open-Meteo (бесплатно, без ключа)."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={CITY_LAT}&longitude={CITY_LON}"
            f"&current_weather=true"
            f"&hourly=precipitation_probability"
            f"&forecast_days=1"
        )
        data = requests.get(url, timeout=10).json()
        cw = data["current_weather"]
        temp = cw["temperature"]
        wind = cw["windspeed"]

        # Описание погоды по коду
        code = cw.get("weathercode", 0)
        if code == 0:
            desc = "ясно"
        elif code in [1, 2, 3]:
            desc = "облачно"
        elif code in [45, 48]:
            desc = "туман"
        elif code in [51, 53, 55, 61, 63, 65]:
            desc = "дождь"
        elif code in [71, 73, 75, 77]:
            desc = "снег"
        elif code in [80, 81, 82]:
            desc = "ливень"
        elif code in [95, 96, 99]:
            desc = "гроза"
        else:
            desc = "переменная облачность"

        return f"{CITY_NAME}: {temp}°C, {desc}, ветер {wind} км/ч"
    except Exception as e:
        return f"{CITY_NAME}: данные недоступны"
