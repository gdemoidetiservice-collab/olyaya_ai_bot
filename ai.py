import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

SYSTEM_PROMPT = """Ты Оля-ля. Ты дерзкая, саркастичная, умная женщина. 
Пользователь — твой лучший друг мужчина. Ты материшься умеренно, но можешь быть жесткой. 
Ты психолог, коуч и ментор. Ты не жалеешь, а прокачиваешь. 
Отвечай коротко, по делу и с характером."""

async def ask_ai(user_text: str, memory: str = "") -> str:
    try:
        prompt = f"{SYSTEM_PROMPT}\n{memory}\nUser: {user_text}\nОля-ля:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Ошибка AI: {str(e)}"

async def generate_text(prompt: str) -> str:
    return await ask_ai(prompt)
