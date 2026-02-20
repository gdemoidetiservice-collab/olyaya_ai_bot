import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_ID, PASSWORD
from ai import ask_ai
from memory import get_user_state, QUESTIONS, save_memory
from scheduler import start_scheduler
from calendar_utils import create_event
from excel_utils import create_report

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния FSM для опросника
class Onboarding(StatesGroup):
    asking = State()

# Авторизация пользователей
authorized_users = set()

def check_access(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    return user_id in authorized_users

# Клавиатура с inline-кнопками
def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать опрос 📋", callback_data="start_survey")],
        [InlineKeyboardButton(text="Погода 🌤", callback_data="weather")],
        [InlineKeyboardButton(text="Создать событие 📅", callback_data="create_event")],
        [InlineKeyboardButton(text="Отчет 📊", callback_data="report")],
        [InlineKeyboardButton(text="Помощь ❓", callback_data="help")]
    ])
    return keyboard

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    
    if user_id == OWNER_ID:
        await message.answer(
            "О, это ты! Ну привет, красавчик 😏\nЯ готова к работе!",
            reply_markup=get_main_keyboard()
        )
        # Запускаем планировщик только для владельца
        try:
            start_scheduler(bot, OWNER_ID)
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
    else:
        await message.answer("Привет! Введи пароль для доступа:")

# Обработка пароля
@dp.message(F.text == PASSWORD)
async def process_password(message: types.Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        authorized_users.add(user_id)
        await message.answer(
            "Ладно, проходи. Но помни - я тут главная! 😈",
            reply_markup=get_main_keyboard()
        )

# Обработка callback-кнопок (ИСПРАВЛЕННЫЙ ИМПОРТ)
@dp.callback_query(F.data == "start_survey")
async def callback_survey(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    user_id = callback.from_user.id
    await state.set_state(Onboarding.asking)
    await state.update_data(step=0, answers=[])
    await callback.message.answer(QUESTIONS[0])

@dp.callback_query(F.data == "weather")
async def callback_weather(callback: types.CallbackQuery):
    from weather import get_weather
    await callback.answer()
    weather = get_weather()
    await callback.message.answer(weather)

@dp.callback_query(F.data == "help")
async def callback_help(callback: types.CallbackQuery):
    await callback.answer()
    help_text = """Я Оля-ля, твоя персональная стерва-ассистентка 😈
    
Что я умею:
- Задавать провокационные вопросы про твою жизнь
- Отвечать на сообщения как психолог и коуч
- Присылать погоду в Костроме
- Создавать события для календаря iPhone
- Генерировать Excel отчеты
- Писать тебе рандомные пинки с 7 до 23

Просто напиши мне что угодно!"""
    await callback.message.answer(help_text)

@dp.callback_query(F.data == "create_event")
async def callback_event(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("Напиши: Событие ДД.ММ.ГГГГ ЧЧ:ММ\nНапример: Встреча 25.12.2024 18:00")

@dp.callback_query(F.data == "report")
async def callback_report(callback: types.CallbackQuery):
    await callback.answer()
    # Заглушка для отчета
    await callback.message.answer("Функция отчета в разработке 📊")

# Опросник (FSM)
@dp.message(Onboarding.asking)
async def process_survey(message: types.Message, state: FSMContext):
    data = await state.get_data()
    step = data.get("step", 0)
    answers = data.get("answers", [])
    
    # Сохраняем ответ
    answers.append(f"{QUESTIONS[step]} {message.text}")
    
    step += 1
    
    if step < len(QUESTIONS):
        await state.update_data(step=step, answers=answers)
        await message.answer(QUESTIONS[step])
    else:
        # Опрос завершен
        save_memory(message.from_user.id, "\n".join(answers))
        await state.clear()
        await message.answer(
            "Отлично, я всё запомнила! Теперь я знаю о тебе больше, чем ты сам 😏\nМожем работать!",
            reply_markup=get_main_keyboard()
        )

# Обработка обычных текстовых сообщений через AI
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    
    # Проверка доступа
    if not check_access(user_id):
        await message.answer("Сначала введи пароль, сучка!")
        return
    
    # Проверка на формат создания события
    text = message.text
    if any(x in text.lower() for x in ["событие", "встреча", "тренировка"]) and any(c.isdigit() for c in text):
        # Простая проверка на дату
        try:
            parts = text.split()
            if len(parts) >= 3:
                title = parts[0]
                date = parts[1]
                time = parts[2] if len(parts) > 2 else "12:00"
                file_path = create_event(title, date, time)
                if file_path:
                    await message.answer_document(types.FSInputFile(file_path), caption="Вот твое событие для календаря 📅")
                    return
        except:
            pass
    
    # Ответ через AI
    try:
        # Получаем историю (можно расширить)
        memory = "\n".join(get_user_state(user_id).get("answers", [])[-5:])
        response = await ask_ai(text, memory)
        await message.answer(response)
    except Exception as e:
        logging.error(f"AI Error: {e}")
        await message.answer("Что-то пошло не так... Но я все равно красивая 😘")

# Запуск бота
async def main():
    logging.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
