import asyncio
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT
)

# Чат-сессии с историей для каждого пользователя
chat_sessions: dict = {}


def get_chat(user_id: int):
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


async def ask_ai(user_id: int, text: str) -> str:
    try:
        chat = get_chat(user_id)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, chat.send_message, text)
        return response.text
    except Exception as e:
        return _handle_error(e)


async def ask_ai_simple(text: str) -> str:
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, text)
        return response.text
    except Exception as e:
        return _handle_error(e)


def _handle_error(e: Exception) -> str:
    err = str(e)
    logger.error(f"Gemini error: {err[:200]}")
    if "429" in err or "quota" in err.lower() or "rate" in err.lower():
        return "Слишком много запросов подряд. Подожди 30 секунд и напиши снова."
    if "403" in err and "leaked" in err.lower():
        return "API ключ скомпрометирован — создай новый на aistudio.google.com и обнови в Railway Variables."
    if "403" in err:
        return "Ошибка доступа к Gemini. Проверь GEMINI_API_KEY в Railway Variables."
    if "404" in err:
        return "Модель Gemini недоступна. Проверь переменную GEMINI_MODEL в Railway Variables."
    return f"Ошибка Gemini: {err[:100]}"
