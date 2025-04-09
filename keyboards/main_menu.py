from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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

back_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")],
        [KeyboardButton(text="🏠 Главное меню")]
    ],
    resize_keyboard=True
)
