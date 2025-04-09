from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Кнопки «Назад» и «Главное меню» (внизу подменю)
back_buttons = [
    [KeyboardButton(text="🔙 Назад")],
    [KeyboardButton(text="🏠 Главное меню")]
]

# Подменю услуг
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
    ] + back_buttons,
    resize_keyboard=True
)
