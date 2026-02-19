import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

OWNER_ID = int(os.getenv("OWNER_ID", "760163261"))
ACCESS_PASSWORD = os.getenv("PASSWORD", "salampopolam")

# Модель Gemini — можно переопределить через Railway Variables
# Проверенные бесплатные варианты: gemini-1.5-flash, gemini-1.5-pro
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Кострома
CITY_LAT = 57.77
CITY_LON = 40.93
CITY_NAME = "Кострома"
