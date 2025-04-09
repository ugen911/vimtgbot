from aiogram import Router, types, F
from config import ADMINS
from keyboards.main_menu import main_menu
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()

user_states = {}

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(F.text == "📋 Запись на экскурсию")
async def start_excursion_form(message: types.Message):
    user_states[message.from_user.id] = {"step": "phone"}
    await message.answer("📋 Для записи на экскурсию, пожалуйста, введите номер телефона:")

@router.message()
async def handle_excursion_form(message: types.Message):
    uid = message.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    if state["step"] == "phone":
        phone = message.text.strip()
        if not is_valid_phone(phone):
            await message.answer("❌ Неверный номер. Допустимые форматы:\n+7XXXXXXXXXX, 8XXXXXXXXXX или 2XXXXXX")
            return
        state["phone"] = phone
        state["step"] = "name"
        await message.answer("Введите ваше имя (необязательно):", reply_markup=skip_keyboard)

    elif state["step"] == "name":
        name = message.text.strip()
        state["name"] = name if name.lower() != "пропустить" else "—"
        state["step"] = "comment"
        await message.answer("Оставьте сообщение (необязательно):", reply_markup=skip_keyboard)

    elif state["step"] == "comment":
        comment = message.text.strip()
        state["comment"] = comment if comment.lower() != "пропустить" else "—"
        await finish_excursion_form(message, state)
        del user_states[uid]

def is_valid_phone(phone: str) -> bool:
    phone = phone.replace(" ", "")
    return (
        re.fullmatch(r"(\+7|8)\d{10}", phone) or
        re.fullmatch(r"2\d{6}", phone)
    )

async def finish_excursion_form(message: types.Message, data: dict):
    name = data.get("name", "—")
    comment = data.get("comment", "—")
    phone = data["phone"]

    msg = (
        f"📋 <b>Новая заявка на экскурсию</b>\n\n"
        f"☎️ <b>Телефон:</b> {phone}\n"
        f"👤 <b>Имя:</b> {name}\n"
        f"💬 <b>Сообщение:</b> {comment}"
    )

    await message.answer("✅ Заявка отправлена! Мы скоро с вами свяжемся.", reply_markup=main_menu)

    # Рассылка администраторам
    for admin in ADMINS:
        try:
            await message.bot.send_message(admin, msg)
        except Exception:
            pass  # игнорируем ошибки, если пользователь не в чате
