"""
Память пользователя — хранит профиль и историю в памяти процесса.
При рестарте бота данные сбрасываются (для персистентности нужна БД).
"""

# Профили пользователей: user_id -> dict
user_profiles = {}

# Статус онбординга: user_id -> {"step": int, "answers": list}
onboarding_states = {}

# Задачи: user_id -> list of {"title": str, "dt": str}
user_tasks = {}


def get_profile(user_id: int) -> dict:
    if user_id not in user_profiles:
        user_profiles[user_id] = {}
    return user_profiles[user_id]


def save_profile_answer(user_id: int, question: str, answer: str):
    profile = get_profile(user_id)
    profile[question] = answer


def get_profile_summary(user_id: int) -> str:
    profile = get_profile(user_id)
    if not profile:
        return ""
    lines = ["Что я знаю о пользователе:"]
    for q, a in profile.items():
        lines.append(f"- {q}: {a}")
    return "\n".join(lines)


def is_onboarding(user_id: int) -> bool:
    return user_id in onboarding_states


def start_onboarding(user_id: int):
    onboarding_states[user_id] = {"step": 0, "answers": []}


def get_onboarding_step(user_id: int) -> int:
    return onboarding_states.get(user_id, {}).get("step", 0)


def save_onboarding_answer(user_id: int, question: str, answer: str):
    save_profile_answer(user_id, question, answer)
    if user_id in onboarding_states:
        onboarding_states[user_id]["step"] += 1


def finish_onboarding(user_id: int):
    onboarding_states.pop(user_id, None)


def add_task(user_id: int, title: str, dt: str = ""):
    if user_id not in user_tasks:
        user_tasks[user_id] = []
    user_tasks[user_id].append({"title": title, "dt": dt})


def get_tasks(user_id: int) -> list:
    return user_tasks.get(user_id, [])


def clear_tasks(user_id: int):
    user_tasks[user_id] = []
