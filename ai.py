import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

# gemini-1.5-flash-8b — реально бесплатная модель (1500 запросов/день, 15 rpm)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",
    system_instruction=SYSTEM_PROMPT
)

# Хранилище чат-сессий (память разговора)
chat_sessions = {}


def get_chat(user_id: int):
    """Возвращает или создаёт чат-сессию для пользователя."""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


async def ask_ai(user_id: int, text: str) -> str:
    """Отправляет сообщение в Gemini и возвращает ответ."""
    try:
        chat = get_chat(user_id)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, chat.send_message, text)
        return response.text
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return "Минуту, слишком много запросов сразу. Подожди секунд 30 и напиши снова."
        if "403" in err:
            return "Проблема с API ключом. Проверь GEMINI_API_KEY в Railway Variables."
        return f"Ошибка AI: {e}"


async def ask_ai_simple(text: str) -> str:
    """Простой запрос без истории (для системных сообщений)."""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, text)
        return response.text
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            return "Слишком много запросов, подожди немного."
        if "403" in err:
            return "Проблема с API ключом."
        return f"Ошибка AI: {e}"
