import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

# Модель с реальным бесплатным тарифом
# gemini-1.5-flash — 1500 req/day, работает через v1 API
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# Хранилище чат-сессий (память разговора)
chat_sessions = {}


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
    if "429" in err or "quota" in err.lower():
        return "Слишком много запросов подряд. Подожди 30 секунд и напиши снова."
    if "403" in err and "leaked" in err.lower():
        return "API ключ скомпрометирован. Создай новый в aistudio.google.com и обнови в Railway Variables."
    if "403" in err:
        return "Проблема с API ключом. Проверь GEMINI_API_KEY в Railway Variables."
    if "404" in err:
        return "Модель недоступна. Обратись к разработчику."
    return f"Ошибка AI: {err[:200]}"
