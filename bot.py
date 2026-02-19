"""
Оля-ля — дерзкая цифровая ассистентка.
Главный файл бота.
"""
import asyncio
import logging
import re
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID, ACCESS_PASSWORD, GEMINI_API_KEY
from ai import ask_ai, ask_ai_simple
from memory import (
    get_profile, get_profile_summary,
    is_onboarding, start_onboarding,
    get_onboarding_step, save_onboarding_answer, finish_onboarding,
    add_task, get_tasks
)
from prompts import ONBOARDING_QUESTIONS
from calendar_utils import save_ics
from excel_utils import create_report
from scheduler import start_scheduler

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан! Добавьте его в переменные окружения Railway.")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан! Добавьте его в переменные окружения Railway.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Авторизованные пользователи (не владелец)
authorized_users: set = set()


def has_access(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in authorized_users


# ============================================================
# СТАРТ
# ============================================================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    uid = message.from_user.id

    if uid == OWNER_ID:
        await message.answer(
            "О, это ты. Ну наконец-то. 🙄\n\n"
            "Я Оля-ля — твоя личная цифровая стерва и лучшая подруга.\n"
            "Пиши мне что угодно.\n\n"
            "Если хочешь пройти знакомство — напиши /знакомство\n"
            "Задачи — просто напиши 'запиши [задача] [время]'\n"
            "Отчёт — /отчет\n"
            "Помощь — /помощь"
        )
    elif has_access(uid):
        await message.answer("Ты уже авторизован. Пиши.")
    else:
        await message.answer("Пароль давай. Или иди мимо.")


@dp.message(Command("помощь"))
async def cmd_help(message: Message):
    if not has_access(message.from_user.id):
        return
    await message.answer(
        "Что я умею:\n\n"
        "• Просто пиши — отвечу как психолог, коуч и подруга\n"
        "• /знакомство — пройти опросник\n"
        "• запиши [задача] [дата/время] — создам задачу и .ics для iPhone\n"
        "• мои задачи — список задач\n"
        "• /отчет — Excel файл со всем\n"
        "• погода — погода в Костроме\n"
        "• найди [запрос] — поиск в интернете (если подключен)\n\n"
        "Утром в 7:00 — приветствие и задачи.\n"
        "В 22:00 — разбор дня.\n"
        "Днём буду писать сама 😈"
    )


# ============================================================
# АВТОРИЗАЦИЯ ЧУЖИХ
# ============================================================

@dp.message(F.text)
async def handle_message(message: Message):
    uid = message.from_user.id
    text = message.text.strip()

    # Авторизация
    if not has_access(uid):
        if text == ACCESS_PASSWORD:
            authorized_users.add(uid)
            await message.answer("Ладно. Проходи. Только не надоедай.")
        else:
            await message.answer("Пароль. Или вали.")
        return

    # ============================================================
    # ОНБОРДИНГ
    # ============================================================
    if is_onboarding(uid):
        step = get_onboarding_step(uid)
        if step < len(ONBOARDING_QUESTIONS):
            question = ONBOARDING_QUESTIONS[step]
            save_onboarding_answer(uid, question, text)
            next_step = get_onboarding_step(uid)
            if next_step < len(ONBOARDING_QUESTIONS):
                # Иногда добавляем короткий комментарий от AI
                if next_step % 3 == 0:
                    comment_prompt = (
                        f"Пользователь ответил на вопрос '{question}': '{text}'. "
                        f"Дай короткий саркастичный комментарий (1 предложение), "
                        f"затем задай следующий вопрос: '{ONBOARDING_QUESTIONS[next_step]}'"
                    )
                    response = await ask_ai_simple(comment_prompt)
                    await message.answer(response)
                else:
                    await message.answer(ONBOARDING_QUESTIONS[next_step])
            else:
                finish_onboarding(uid)
                summary = get_profile_summary(uid)
                response = await ask_ai_simple(
                    f"Онбординг завершён. Вот профиль пользователя:\n{summary}\n\n"
                    f"Напиши краткое резюме что ты узнала о нём, в стиле Оли-ля. "
                    f"Саркастично, с теплом, честно."
                )
                await message.answer(response)
        return

    # ============================================================
    # КОМАНДЫ ЧЕРЕЗ ТЕКСТ
    # ============================================================

    text_lower = text.lower()

    # --- Знакомство ---
    if any(kw in text_lower for kw in ["/знакомство", "знакомство", "пройти опрос", "расскажи о себе"]):
        start_onboarding(uid)
        await message.answer(ONBOARDING_QUESTIONS[0])
        return

    # --- Задачи: запись ---
    if any(kw in text_lower for kw in ["запиши", "добавь задачу", "напомни", "создай задачу", "поставь напоминание"]):
        await handle_task_creation(message, uid, text)
        return

    # --- Задачи: просмотр ---
    if any(kw in text_lower for kw in ["мои задачи", "список задач", "что у меня", "что сегодня"]):
        tasks = get_tasks(uid)
        if not tasks:
            await message.answer("Задач нет. Или ты их не записал — что более вероятно.")
        else:
            lines = ["Твои задачи:"]
            for i, t in enumerate(tasks, 1):
                line = f"{i}. {t['title']}"
                if t.get("dt"):
                    line += f" — {t['dt']}"
                lines.append(line)
            await message.answer("\n".join(lines))
        return

    # --- Отчёт ---
    if any(kw in text_lower for kw in ["/отчет", "отчет", "отчёт", "excel", "экспорт"]):
        await send_excel_report(message, uid)
        return

    # --- Погода ---
    if any(kw in text_lower for kw in ["погода", "температура", "как там на улице"]):
        from weather import get_weather
        weather = get_weather()
        prompt = f"Погода в Костроме: {weather}. Прокомментируй в своём стиле, коротко."
        response = await ask_ai(uid, prompt)
        await message.answer(response)
        return

    # ============================================================
    # ОСНОВНОЙ ИИ ДИАЛОГ
    # ============================================================

    # Добавляем контекст профиля при первом сообщении
    profile_summary = get_profile_summary(uid)
    if profile_summary and text:
        # Добавляем профиль как контекст только если он не пустой
        full_prompt = f"[Контекст о пользователе: {profile_summary}]\n\nПользователь пишет: {text}"
    else:
        full_prompt = text

    response = await ask_ai(uid, full_prompt)
    await message.answer(response)


# ============================================================
# СОЗДАНИЕ ЗАДАЧИ
# ============================================================

async def handle_task_creation(message: Message, uid: int, text: str):
    """Парсит задачу и создаёт .ics файл."""
    # Используем AI для парсинга задачи
    parse_prompt = (
        f"Из текста '{text}' извлеки: название задачи и дату/время (если есть). "
        f"Ответь ТОЛЬКО в формате JSON: {{\"title\": \"...\", \"datetime\": \"YYYY-MM-DD HH:MM или пусто\"}}"
        f"Не добавляй ничего лишнего, только JSON."
    )
    try:
        parse_response = await ask_ai_simple(parse_prompt)
        # Чистим ответ от markdown
        clean = re.sub(r"```json|```", "", parse_response).strip()
        import json
        task_data = json.loads(clean)
        title = task_data.get("title", text)
        dt_str = task_data.get("datetime", "")
    except Exception:
        title = text
        dt_str = ""

    # Парсим дату
    dt_obj = None
    if dt_str:
        for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d"]:
            try:
                dt_obj = datetime.strptime(dt_str, fmt)
                break
            except ValueError:
                pass

    # Сохраняем задачу
    add_task(uid, title, dt_str)

    # Создаём .ics
    if dt_obj:
        try:
            ics_path = save_ics(title, dt_obj, f"Задача от Оля-ля бота")
            file = FSInputFile(ics_path, filename="task.ics")
            await message.answer_document(
                file,
                caption=f"✅ Записала: **{title}**\n📅 {dt_str}\n\nОткрой файл на iPhone — добавится в Календарь."
            )
        except Exception as e:
            logger.error(f"ICS error: {e}")
            await message.answer(f"✅ Записала: {title} ({dt_str})\nФайл календаря не удалось создать.")
    else:
        await message.answer(f"✅ Записала: {title}\nВремя не указано — ты и сам помнишь, надеюсь.")


# ============================================================
# EXCEL ОТЧЁТ
# ============================================================

async def send_excel_report(message: Message, uid: int):
    tasks = get_tasks(uid)
    profile = get_profile(uid)
    try:
        filepath = create_report(tasks, profile)
        if filepath:
            file = FSInputFile(filepath, filename="olya_report.xlsx")
            await message.answer_document(file, caption="Держи свой отчёт. Много там пустого — сам виноват.")
        else:
            await message.answer("openpyxl не установлен. Отчёт недоступен.")
    except Exception as e:
        logger.error(f"Excel error: {e}")
        await message.answer(f"Ошибка при создании отчёта: {e}")


# ============================================================
# ЗАПУСК
# ============================================================

async def main():
    logger.info("Запуск Оля-ля бота...")

    # Удаляем вебхук и очищаем очередь — решает TelegramConflictError
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Вебхук удалён, очередь очищена")

    # Запускаем планировщик
    start_scheduler(bot)
    logger.info("Планировщик запущен")

    # Запускаем polling
    logger.info("Polling запущен. Бот готов к работе.")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
