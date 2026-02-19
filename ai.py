import asyncio
import google.generativeai as genai
from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

# Перебираем модели по приоритету — найдём рабочую
MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-pro",
]

def _create_model(model_name: str):
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=SYSTEM_PROMPT
    )

def _find_working_model():
    """Перебирает модели и возвращает первую рабочую."""
    for name in MODELS_TO_TRY:
        try:
            m = _create_model(name)
            # Тестовый запрос
            m.generate_content("ping")
            print(f"[AI] Рабочая модель: {name}")
            return m, name
        except Exception as e:
            print(f"[AI] Модель {name} недоступна: {str(e)[:80]}")
    return None, None

# Инициализация при старте
_model = None
_model_name = None
chat_sessions = {}

def get_model():
    global _model, _model_name
    if _model is None:
        _model, _model_name = _find_working_model()
    return _model

def get_chat(user_id: int):
    m = get_model()
    if m is None:
        return None
    if user_id not in chat_sessions:
        chat_sessions[user_id] = m.start_chat(history=[])
    return chat_sessions[user_id]

async def ask_ai(user_id: int, text: str) -> str:
    try:
        chat = get_chat(user_id)
        if chat is None:
            return "Gemini API недоступен. Проверь GEMINI_API_KEY в Railway Variables."
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, chat.send_message, text)
        return response.text
    except Exception as e:
        return _handle_error(e)

async def ask_ai_simple(text: str) -> str:
    try:
        m = get_model()
        if m is None:
            return "Gemini API недоступен."
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, m.generate_content, text)
        return response.text
    except Exception as e:
        return _handle_error(e)

def _handle_error(e: Exception) -> str:
    err = str(e)
    if "429" in err or "quota" in err.lower():
        return "Слишком много запросов. Подожди 30 секунд и напиши снова."
    if "403" in err and "leaked" in err.lower():
        return "API ключ скомпрометирован. Создай новый на aistudio.google.com и обнови в Railway Variables."
    if "403" in err:
        return "Ошибка доступа к Gemini. Проверь GEMINI_API_KEY в Railway Variables."
    if "404" in err:
        global _model, _model_name
        _model = None  # сбросим — попробуем другую модель при следующем запросе
        chat_sessions.clear()
        return "Переключаю модель... Напиши ещё раз."
    return f"Ошибка: {err[:150]}"
