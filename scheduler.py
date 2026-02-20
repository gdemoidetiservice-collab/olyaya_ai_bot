"""
Планировщик сообщений:
- 07:00 — утреннее сообщение
- 22:00 — вечерний разнос дня
- 8-22 — случайные сообщения (3-7 в день), только из готового списка (без AI)
"""
import random
import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from config import OWNER_ID
from weather import get_weather
from prompts import RANDOM_MESSAGES, EVENING_PROMPT
from ai import ask_ai_simple
from memory import get_tasks

logger = logging.getLogger(__name__)


def start_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # === Утреннее сообщение в 07:00 ===
    @scheduler.scheduled_job(CronTrigger(hour=7, minute=0))
    async def morning_message():
        try:
            weather = get_weather()
            tasks = get_tasks(OWNER_ID)
            tasks_text = ""
            if tasks:
                tasks_text = "\nТвои задачи:\n" + "\n".join(
                    f"• {t['title']}" + (f" ({t['dt']})" if t['dt'] else "")
                    for t in tasks
                )
            else:
                tasks_text = "\nЗадач нет — либо ты всё сделал, либо ничего не планировал."

            prompt = (
                f"Напиши утреннее саркастическое приветствие для своего лучшего друга. "
                f"Погода: {weather}. {tasks_text}. "
                f"Стиль: дерзко, с матом, мотивирующе. Коротко — 3-5 предложений."
            )
            text = await ask_ai_simple(prompt)
            await bot.send_message(OWNER_ID, text)
        except Exception as e:
            logger.error(f"Morning message error: {e}")

    # === Вечернее сообщение в 22:00 ===
    @scheduler.scheduled_job(CronTrigger(hour=22, minute=0))
    async def evening_message():
        try:
            prompt = EVENING_PROMPT
            text = await ask_ai_simple(prompt)
            await bot.send_message(OWNER_ID, text)
        except Exception as e:
            logger.error(f"Evening message error: {e}")

    # === Случайные сообщения — только из готового списка, без AI ===
    def schedule_random_messages():
        count = random.randint(3, 7)  # уменьшили максимум с 10 до 7
        today = datetime.now().replace(second=0, microsecond=0)

        scheduled_times = set()
        attempts = 0
        while len(scheduled_times) < count and attempts < 50:
            attempts += 1
            hour = random.randint(8, 21)
            minute = random.randint(0, 59)
            if (hour, minute) in scheduled_times:
                continue
            msg_time = today.replace(hour=hour, minute=minute)
            if msg_time <= datetime.now():
                continue
            scheduled_times.add((hour, minute))

            # Только готовый текст — никаких AI-запросов в случайных сообщениях
            msg_text = random.choice(RANDOM_MESSAGES)

            async def send_random(text=msg_text):
                try:
                    await bot.send_message(OWNER_ID, text)
                except Exception as e:
                    logger.error(f"Random message error: {e}")

            scheduler.add_job(
                send_random,
                trigger=DateTrigger(run_date=msg_time),
                id=f"random_{hour}_{minute}_{attempts}"
            )

        logger.info(f"Запланировано {len(scheduled_times)} случайных сообщений на сегодня")

    schedule_random_messages()

    @scheduler.scheduled_job(CronTrigger(hour=0, minute=1))
    async def reschedule_daily():
        schedule_random_messages()

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler
