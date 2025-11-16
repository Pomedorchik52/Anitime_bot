import asyncio
import logging
import random

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = ""
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура
builder = ReplyKeyboardBuilder()
builder.add(
    KeyboardButton(text="help"),
    KeyboardButton(text="contact"),
    KeyboardButton(text="random")
)
builder.adjust(2, 1)
reply_markup = builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# Список аниме — никаких экранирований больше НЕ НУЖНО
ANIME_LIST = [
    "Атака титанов",
    "Тетрадь смерти",
    "Ван-Пис",
    "Наруто",
    "Ангел по соседству",
    "Аля иногда кокетничает со мной по-русски",
    "Детектив уже мёртв",
    "Берсерк",
    "Необьятный океан",
    "Невероятные приключения ДжоДжо",
    "Такийский гуль",
    "Мастер меча онлайн",
    "Внук мудреца",
    "Моя геройская академия",
    "Доктор Стоун",
    "Волейбол!!",
    "Евангелион",
    "Паразит: Учение о жизни",
    "Магическая битва",
    "Клинок, рассекающий демонов",
    "Стальной алхимик",
    "Звездное дитя"
]

# /start
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    text = (
        "<b>Привет, дорогой пользователь!</b>\n\n"
        "Я помогу тебе выбрать случайное аниме или связаться с разработчиком."
    )
    await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)

# /help
@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    text = (
        "<b>Список команд:</b>\n"
        "/start — Запустить бота\n"
        "/help — Показать это меню\n"
        "/random — Получить случайное аниме\n"
        "/contact — Связаться с разработчиком\n\n"
        "Нажми кнопки ниже"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)

# /random
@dp.message(Command(commands=["random"]))
async def cmd_random(message: Message):
    anime = random.choice(ANIME_LIST)
    text = f"<b>Случайное аниме:</b>\n{anime}"
    await message.answer(text, parse_mode="HTML")

# /contact — каждая строка с новой строки
@dp.message(Command(commands=["contact"]))
async def cmd_contact(message: Message):
    text = (
        "<b>Связь с разработчиком:</b>\n"
        "Telegram: @Pomedorchik52\n"
        "Email: sldfjskf@gmail.com\n"
        "GitHub: github.com/Pomedorchik52"
    )
    await message.answer(text, parse_mode="HTML")

# Кнопки
@dp.message(lambda msg: msg.text and msg.text.lower() == "help")
async def btn_help(message: Message):
    await cmd_help(message)

@dp.message(lambda msg: msg.text and msg.text.lower() == "contact")
async def btn_contact(message: Message):
    await cmd_contact(message)

@dp.message(lambda msg: msg.text and msg.text.lower() == "random")
async def btn_random(message: Message):
    await cmd_random(message)

# Запуск
async def main():
    print("Бот запущен...")
    print("Бот готов к работе...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())