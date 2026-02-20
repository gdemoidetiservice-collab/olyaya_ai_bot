import asyncio
import logging
import google.generativeai as genai
from google.generativeai import types
from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Явно указываем v1 API (не v1beta)
genai.configure(
    api_key=GEMINI_API_KEY,
    client_options={"api_endpoint": "generativelanguage.googleapis.com"}
)

# Перебор моделей — первая рабочая победит
CANDIDATE_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
]

_model = None
chat_sessions: dict = {}


def _init_model():
    global _model
    # Пробуем каждую модель — просто создаём объект, без тестового запроса
    from config import GEMINI_MODEL
    # Сначала пробуем модель из переменной окружения
    try:
        _model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT
        )
        logger.info(f"Модель из переменной: {GEMINI_MODEL}")
        return
    except Exception as e:
        logger.warning(f"Не смогли создать {GEMINI_MODEL}: {e}")

    # Fallback — пробуем список
    for name in CANDIDATE_MODELS:
        try:
            _model = genai.GenerativeModel(
                model_name=name,
                system_instruction=SYSTEM_PROMPT
            )
            logger.info(f"Используем модель: {name}")
            return
        except Exception as e:
            logger.warning(f"Модель {name} не создана: {e}")

    logger.error("Ни одна модель не доступна!")
    _model = None


def get_model():
    global _model
    if _model is None:
        _init_model()
    return _model


def get_chat(user_id: int):
    m = get_model()
    if m is None:
        return None
    if user_id not in chat_sessions:
        chat_sessions[user_id] = m.start_chat(history=[])
    return chat_sessions[user_id]


async def _call_with_retry(fn, *args, max_retries=4):
    delay = 15
    for attempt in range(max_retries):
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, fn, *args)
        except Exception as e:
            err = str(e)
            if "404" in err:
                # Модель недоступна — сбрасываем и пробуем следующую
                global _model
                _model = None
                chat_sessions.clear()
                _init_model()
                if attempt < max_retries - 1:
                    continue
            if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit, жду {delay}s")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 60)
                    continue
            raise


async def ask_ai(user_id: int, text: str) -> str:
    try:
        chat = get_chat(user_id)
        if chat is None:
            return "Gemini недоступен. Проверь GEMINI_API_KEY в Railway Variables."
        response = await _call_with_retry(chat.send_message, text)
        return response.text
    except Exception as e:
        return _handle_error(e)


async def ask_ai_simple(text: str) -> str:
    try:
        m = get_model()
        if m is None:
            return "Gemini недоступен. Проверь GEMINI_API_KEY в Railway Variables."
        response = await _call_with_retry(m.generate_content, text)
        return response.text
    except Exception as e:
        return _handle_error(e)


def _handle_error(e: Exception) -> str:
    err = str(e)
    logger.error(f"Gemini error: {err[:300]}")
    if "429" in err or "quota" in err.lower():
        return "Gemini перегружен, попробуй написать через минуту."
    if "403" in err and "leaked" in err.lower():
        return "API ключ скомпрометирован — создай новый на aistudio.google.com."
    if "403" in err:
        return "Ошибка доступа. Проверь GEMINI_API_KEY в Railway Variables."
    if "404" in err:
        return "Модель Gemini недоступна. Попробуй добавить переменную GEMINI_MODEL=gemini-2.0-flash-lite в Railway Variables."
    return f"Ошибка: {err[:150]}"
