import google.generativeai as genai
from config import GEMINI_API_KEY
from prompts import SYSTEM_PROMPT

genai.configure(api_key=GEMINI_API_KEY)

# Используем gemini-2.0-flash — бесплатная актуальная модель
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
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
        response = chat.send_message(text)
        return response.text
    except Exception as e:
        return f"Ошибка AI: {e}"


async def ask_ai_simple(text: str) -> str:
    """Простой запрос без истории (для системных сообщений)."""
    try:
        response = model.generate_content(text)
        return response.text
    except Exception as e:
        return f"Ошибка AI: {e}"
