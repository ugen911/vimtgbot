import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Главное меню ===
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Услуги"), KeyboardButton(text="📰 Анонсы")],
        [KeyboardButton(text="📋 Запись на экскурсию")],
        [KeyboardButton(text="🌐 Онлайн экскурсия")],
        [KeyboardButton(text="📆 Расписание занятий")],
        [KeyboardButton(text="🧑‍🏫 Педагоги")],
        [KeyboardButton(text="🍎 Меню")]
    ],
    resize_keyboard=True
)

# === Кнопки навигации ===
back_menu = [
    [KeyboardButton(text="🔙 Назад")],
    [KeyboardButton(text="🏠 Главное меню")]
]

# === Подменю: Услуги ===
services_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏫 Детский сад полного дня")],
        [KeyboardButton(text="🗣 Логопед"), KeyboardButton(text="🎤 Запуск речи")],
        [KeyboardButton(text="💆 Логомассаж"), KeyboardButton(text="🧘 Аэройога")],
        [KeyboardButton(text="🧠 Подготовка к школе"), KeyboardButton(text="📚 Скорочтение")],
        [KeyboardButton(text="🎨 Творческая мастерская")],
        [KeyboardButton(text="🧮 Ментальная арифметика")],
        [KeyboardButton(text="👩‍👧 Вместе с мамой"), KeyboardButton(text="💪 Крепыш ОФП")],
        [KeyboardButton(text="🎵 Музыкальная терапия")]
    ] + back_menu,
    resize_keyboard=True
)

# === Подменю: Расписание ===
schedule_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👶 Младшая группа")],
        [KeyboardButton(text="🧒 Старшая группа")]
    ] + back_menu,
    resize_keyboard=True
)

# === Подменю: Педагоги ===
teachers_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧸 Воспитатели")],
        [KeyboardButton(text="📖 Преподаватели")]
    ] + back_menu,
    resize_keyboard=True
)

# === Старт ===
@dp.message(F.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(
        "🏡 <b>Добро пожаловать в детский сад \"Виммельбух\"! 👶</b>\n\n"
        "Выберите интересующий раздел из меню ниже:",
        reply_markup=main_menu
    )

# === Главное меню ===
@dp.message(F.text == "🏠 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏡 Главное меню:", reply_markup=main_menu)

# === Назад (отправляет в главное меню) ===
@dp.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("🔙 Возвращаемся назад:", reply_markup=main_menu)

# === Разделы ===
@dp.message(F.text == "📚 Услуги")
async def show_services(message: types.Message):
    await message.answer("<b>📚 Наши услуги:</b>", reply_markup=services_menu)

@dp.message(F.text == "📆 Расписание занятий")
async def show_schedule(message: types.Message):
    await message.answer("<b>📆 Выберите группу:</b>", reply_markup=schedule_menu)

@dp.message(F.text == "🧑‍🏫 Педагоги")
async def show_teachers(message: types.Message):
    await message.answer("<b>🧑‍🏫 Наши педагоги:</b>", reply_markup=teachers_menu)

# === Временно-заглушки ===
@dp.message(F.text.in_([
    "📰 Анонсы", "📋 Запись на экскурсию", "🌐 Онлайн экскурсия", "🍎 Меню"
]))
async def section_placeholder(message: types.Message):
    await message.answer("🚧 Этот раздел скоро будет доступен! Следите за обновлениями.", reply_markup=main_menu)

# === Пример контента: Аэройога ===
@dp.message(F.text == "🧘 Аэройога")
async def show_aeroyoga_info(message: types.Message):
    await message.answer(
        "<b>🧘 Аэройога</b>\n\n"
        "Весёлые и полезные занятия на полотнах (гамаках).\n"
        "Развивают координацию, гибкость и уверенность.\n"
        "Подходит детям от 3 лет. Занятия проводятся 2 раза в неделю."
    )

# === Заглушка для остальных услуг ===
@dp.message(F.text.regexp(r"^🏫|🗣|🎤|💆|🧠|📚|🎨|🧮|👩‍👧|💪|🎵"))
async def show_service_template(message: types.Message):
    await message.answer(
        f"<b>{message.text}</b>\n\n📌 Описание этой услуги будет добавлено позже.",
        reply_markup=services_menu
    )

# === Заглушка для расписания ===
@dp.message(F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"]))
async def show_schedule_placeholder(message: types.Message):
    await message.answer(
        f"📅 <b>Расписание для {message.text.lower()}</b> появится здесь совсем скоро!",
        reply_markup=schedule_menu
    )

# === Заглушка для педагогов ===
@dp.message(F.text.in_(["🧸 Воспитатели", "📖 Преподаватели"]))
async def show_teachers_placeholder(message: types.Message):
    await message.answer(
        f"👩‍🏫 <b>{message.text}</b>\n\nИнформация о педагогах будет доступна в этом разделе.",
        reply_markup=teachers_menu
    )

# === Запуск бота ===
async def main():
    print("🤖 Бот запущен. Ждёт команд...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
