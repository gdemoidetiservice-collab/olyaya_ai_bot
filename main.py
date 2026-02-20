import os
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID, PASSWORD
from ai import ask_ai
from memory import get_user_state, QUESTIONS, save_memory, get_memory
from scheduler import start_scheduler
from calendar_utils import create_event
from excel_utils import create_report
from weather import get_weather

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Onboarding(StatesGroup):
    asking = State()

class CreateEvent(StatesGroup):
    waiting_for_text = State()

authorized_users = set()

def check_access(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    return user_id in authorized_users

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать опрос 📋", callback_data="start_survey")],
        [InlineKeyboardButton(text="Погода в Костроме 🌤", callback_data="weather")],
        [InlineKeyboardButton(text="Создать событие 📅", callback_data="create_event")],
        [InlineKeyboardButton(text="Отчет 📊", callback_data="report")],
        [InlineKeyboardButton(text="Помощь ❓", callback_data="help")]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if user_id == OWNER_ID:
        await message.answer(
            "О, это ты! Ну привет, красавчик 😏\nЯ твоя персональная стерва-ассистентка!",
            reply_markup=get_main_keyboard()
        )
        try:
            start_scheduler(bot, OWNER_ID)
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
    else:
        await message.answer("Привет! Введи пароль для доступа:")

@dp.message(F.text == PASSWORD)
async def process_password(message: types.Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        authorized_users.add(user_id)
        await message.answer(
            "Ладно, проходи. Но помни - я тут главная! 😈",
            reply_markup=get_main_keyboard()
        )

@dp.callback_query(F.data == "start_survey")
async def callback_survey(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.set_state(Onboarding.asking)
    await state.update_data(step=0, answers=[])
    await callback.message.answer("Начинаем опрос!\n\n" + QUESTIONS[0])

@dp.callback_query(F.data == "weather")
async def callback_weather(callback: types.CallbackQuery):
    await callback.answer()
    weather = get_weather()
    await callback.message.answer(weather)

@dp.callback_query(F.data == "help")
async def callback_help(callback: types.CallbackQuery):
    await callback.answer()
    help_text = """Я Оля-ля, твоя стерва-ассистентка 😈

Что я умею:
• Отвечать на сообщения с сарказмом и матом
• Задавать провокационные вопросы про твою жизнь
• Присылать погоду в Костроме
• Писать рандомные пинки с 7 до 23
• Создавать события для календаря iPhone
• Быть твоим психологом и коучем

Просто напиши мне что угодно!"""
    await callback.message.answer(help_text)

@dp.callback_query(F.data == "create_event")
async def callback_event(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreateEvent.waiting_for_text)
    await callback.message.answer("Напиши: Событие ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: Тренировка 25.12.2024 18:00")

@dp.callback_query(F.data == "report")
async def callback_report(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Отчет пока в разработке 📊")

@dp.message(Onboarding.asking)
async def process_survey(message: types.Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("step", 0)
    answers = data.get("answers", [])
    
    answers.append(f"{QUESTIONS[step]}: {message.text}")
    step += 1
    
    if step < len(QUESTIONS):
        await state.update_data(step=step, answers=answers)
        await message.answer(QUESTIONS[step])
    else:
        save_memory(message.from_user.id, "\n".join(answers))
        await state.clear()
        await message.answer(
            "Отлично, я всё запомнила! Теперь знаю о тебе больше, чем ты сам 😏\nПиши мня что угодно!",
            reply_markup=get_main_keyboard()
        )

@dp.message(CreateEvent.waiting_for_text)
async def process_event(message: types.Message, state: FSMContext):
    await state.clear()
    text = message.text
    
    try:
        parts = text.split()
        if len(parts) >= 3:
            title = parts[0]
            date = parts[1]
            time = parts[2] if len(parts) > 2 else "12:00"
            file_path = create_event(title, date, time)
            if file_path:
                await message.answer_document(FSInputFile(file_path), caption="Вот твое событие 📅")
            else:
                await message.answer("Не удалось создать событие.")
        else:
            await message.answer("Неверный формат. Пример: Тренировка 25.12.2024 18:00")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    
    if not check_access(user_id):
        await message.answer("Сначала введи пароль, сучка!")
        return
    
    # Проверка на формат события
    text = message.text
    if any(x in text.lower() for x in ["событие", "встреча", "тренировка"]) and "." in text:
        try:
            parts = text.split()
            if len(parts) >= 3 and ":" in parts[2]:
                await message.answer("Нажми кнопку 'Создать событие' для этого!")
                return
        except:
            pass
    
    # AI ответ
    try:
        memory = get_memory(user_id)
        response = await ask_ai(text, memory)
        save_memory(user_id, f"User: {text}\nBot: {response}")
        await message.answer(response)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        await message.answer("Что-то пошло не так... Но я все равно красивая 😘")

async def main():
    logging.info("Starting Olya-bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
