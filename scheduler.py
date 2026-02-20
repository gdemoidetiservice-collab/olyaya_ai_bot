import random
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from weather import get_weather

def start_scheduler(bot, user_id: int):
    scheduler = AsyncIOScheduler()
    
    # Утреннее сообщение в 7:00
    async def morning_message():
        weather = get_weather()
        text = f"Доброе утро, сучка! ☀️\n{weather}\nНе тупи сегодня, у тебя есть дела!"
        await bot.send_message(user_id, text)
    
    scheduler.add_job(morning_message, "cron", hour=7, minute=0)
    
    # Рандомные пинки (3-10 раз в день с 7:00 до 23:00)
    async def random_pin():
        pins = [
            "Ты жив вообще? Напиши что-нибудь.",
            "Ты сегодня двигаешься к цели или опять прокрастинируешь?",
            "Когда ты в последний раз нормально отдыхал?",
            "Ты сейчас работаешь или страдаешь хернёй?",
            "Потрахался сегодня? Нет? Так когда планируешь?",
            "Вставай с дивана, там пыль уже образуется!",
            "Ты ел сегодня нормально? Или опять доширак?",
            "Напомни, когда ты в последний раз делал что-то полезное?"
        ]
        await bot.send_message(user_id, random.choice(pins))
    
    # Генерируем случайное количество пинков (3-10)
    pin_count = random.randint(3, 10)
    for _ in range(pin_count):
        hour = random.randint(7, 23)
        minute = random.randint(0, 59)
        scheduler.add_job(random_pin, "cron", hour=hour, minute=minute)
    
    scheduler.start()
    return scheduler
