from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Услуги"), KeyboardButton(text="📰 Анонсы")],
        [KeyboardButton(text="🌐 Онлайн экскурсия")],
        [KeyboardButton(text="📅 Расписание занятий")],
        [KeyboardButton(text="🧑‍🏫 Педагоги")],
        [KeyboardButton(text="🍎 Меню")],
        [KeyboardButton(text="📞 Контакты")],
    ],
    resize_keyboard=True,
)

back_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔙 Назад")]], resize_keyboard=True
)

admin_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Услуги"), KeyboardButton(text="📰 Анонсы")],
        [KeyboardButton(text="🍎 Меню"), KeyboardButton(text="📅 Расписание")],
        [
            KeyboardButton(text="🧑‍🏫 Педагоги"),
            KeyboardButton(text="🌐 Онлайн экскурсия"),
        ],
        [KeyboardButton(text="⚙️ Админы")],
    ],
    resize_keyboard=True,
)
