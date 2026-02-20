import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")  # опционально

OWNER_ID = int(os.getenv("OWNER_ID", "760163261"))
PASSWORD = os.getenv("PASSWORD", "salampopolam")

CITY_LAT = 57.77
CITY_LON = 40.93

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден! Добавьте в .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден! Добавьте в .env")
