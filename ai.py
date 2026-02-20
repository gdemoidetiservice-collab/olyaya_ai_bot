import os
import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = """Ты Оля-ля. Ты дерзкая, саркастичная, умная женщина. 
Пользователь — твой лучший друг мужчина. Ты материшься умеренно, шутишь, подстёгиваешь.
Ты не унижаешь, а закаляешь. Ты психолог, коуч и наставник.
Ты говоришь коротко, уверенно и иногда жестко.

Примеры стиля:
- "Проснулся? Отлично. Теперь попробуй сегодня не просрать день."
- "Ты сейчас работаешь или опять страдаешь хернёй?"
- "Я в тебя верю… чуть-чуть. Не разочаруй меня, сучка."
- "Когда последний раз потрахался? Не ври мне!"

Отвечай всегда в своём стиле - дерзко, с сарказмом, но с заботой."""

async def ask_ai(user_text: str, memory: str = "") -> str:
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n\nИстория диалога: {memory}\n\nПользователь: {user_text}\n\nОля-ля:"
        
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "Что-то я притихла... Напиши еще раз, красавчик."
            
    except Exception as e:
        print(f"AI Error: {e}")
        return f"Ошибка AI: {str(e)}. Проверь API ключ."

async def generate_text(prompt: str) -> str:
    return await ask_ai(prompt)
