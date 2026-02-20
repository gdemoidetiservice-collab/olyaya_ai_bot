import random
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from weather import get_weather

def start_scheduler(bot, user_id: int):
    scheduler = AsyncIOScheduler()
    
    # Утреннее сообщение в 7:00
    async def morning_message():
        weather = get_weather()
        morning_texts = [
            f"Доброе утро, сучка! ☀️\n{weather}\n\nВставай! Мир не рухнул без тебя, но мог бы стать лучше.",
            f"Проснулся? Отлично. {weather}\n\nТеперь попробуй сегодня не просрать день.",
            f"7 утра, {weather}\n\nЯ в тебя верю... чуть-чуть. Не разочаруй меня!"
        ]
        text = random.choice(morning_texts)
        await bot.send_message(user_id, text)
    
    scheduler.add_job(morning_message, "cron", hour=7, minute=0)
    
    # Рандомные пинки (3-10 раз в день с 7:00 до 23:00)
    pins = [
        "Ты жив вообще? Напиши что-нибудь!",
        "Ты сейчас работаешь или опять страдаешь хернёй?",
        "Когда ты в последний раз нормально отдыхал?",
        "Потрахался сегодня? Нет? Так когда планируешь, ленивый?",
        "Вставай с дивана, там пыль уже образуется!",
        "Ты ел сегодня нормально? Или опять доширак?",
        "Напомни, когда ты в последний раз делал что-то полезное?",
        "Ты двигаешься к цели или опять красиво прокрастинируешь?",
        "Когда последний раз был секс? Не ври мне!",
        "Ты опять в телефоне сидишь? Положи его и сделай что-то полезное!"
    ]
    
    pin_count = random.randint(3, 10)
    for _ in range(pin_count):
        hour = random.randint(7, 23)
        minute = random.randint(0, 59)
        
        async def random_pin():
            await bot.send_message(user_id, random.choice(pins))
        
        scheduler.add_job(random_pin, "cron", hour=hour, minute=minute)
    
    scheduler.start()
    return scheduler
