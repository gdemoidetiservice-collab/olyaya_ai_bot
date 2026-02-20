from typing import Dict, Any, List

user_states: Dict[int, Dict[str, Any]] = {}

QUESTIONS = [
    "Привет! Давай знакомиться. Как тебя зовут, красавчик?",
    "Какое у тебя любимое время года?",
    "Какая твоя любимая музыка?",
    "Какие фильмы или сериалы ты любишь?",
    "Как любишь отдыхать?",
    "Какие привычки ты хочешь отслеживать?",
    "В отношениях ли ты сейчас? Если нет, почему расстались?",
    "Когда была последняя близость? Честно!",
    "Что для тебя важно в интимной близости?",
    "Какие позы любишь? Где любишь заниматься этим?",
    "С кем тебе нравится это делать?",
    "Есть ли что-то, что ненавидишь в людях?",
    "Что тебя мотивирует и что раздражает?"
]

def get_user_state(user_id: int) -> Dict:
    if user_id not in user_states:
        user_states[user_id] = {"step": 0, "answers": [], "authorized": False, "profile": {}}
    return user_states[user_id]

def save_memory(user_id: int, text: str):
    state = get_user_state(user_id)
    if "history" not in state:
        state["history"] = []
    state["history"].append(text)
    state["history"] = state["history"][-20:]  # Храним последние 20 сообщений

def get_memory(user_id: int) -> str:
    state = get_user_state(user_id)
    history = state.get("history", [])
    answers = state.get("answers", [])
    return "\n".join(answers[-5:] + history[-5:])
