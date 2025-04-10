from aiogram import Router, types, F
from config import ADMINS
from keyboards.main_menu import main_menu, back_menu
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

user_states = {}

# Используется только на шагах "имя" и "комментарий"
skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить")],
        [KeyboardButton(text="🔙 Назад"), KeyboardButton(text="🏠 Главное меню")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(F.text == "📋 Запись на экскурсию")
async def start_excursion_form(message: types.Message):
    user_states[message.from_user.id] = {"step": "phone"}
    await message.answer(
        "📋 Для записи на экскурсию, пожалуйста, введите номер телефона:",
        reply_markup=back_menu,
    )


@router.message(F.text.in_(["🔙 Назад", "🏠 Главное меню"]))
async def cancel_form(message: types.Message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    if message.text == "🔙 Назад":
        await message.answer("🔙 Возвращаемся назад:", reply_markup=main_menu)
    else:
        await message.answer("🏡 Главное меню:", reply_markup=main_menu)


@router.message()
async def handle_excursion_form(message: types.Message):
    uid = message.from_user.id
    state = user_states.get(uid)

    if not state:
        return

    text = message.text.strip()

    # Защита: если пользователь нажал кнопку другого раздела, отменяем форму
    if text in [
        "📚 Услуги",
        "📰 Анонсы",
        "📋 Запись на экскурсию",
        "🌐 Онлайн экскурсия",
        "📆 Расписание занятий",
        "🧑‍🏫 Педагоги",
        "🍎 Меню",
    ]:
        del user_states[uid]
        return

    if state["step"] == "phone":
        if not is_valid_phone(text):
            await message.answer(
                "❌ Неверный номер. Допустимые форматы:\n+7XXXXXXXXXX, 8XXXXXXXXXX или 2XXXXXX",
                reply_markup=back_menu,
            )
            return
        state["phone"] = text
        state["step"] = "name"
        await message.answer(
            "Введите ваше имя (необязательно):", reply_markup=skip_keyboard
        )

    elif state["step"] == "name":
        state["name"] = text if text.lower() != "пропустить" else "—"
        state["step"] = "comment"
        await message.answer(
            "Оставьте сообщение (необязательно):", reply_markup=skip_keyboard
        )

    elif state["step"] == "comment":
        state["comment"] = text if text.lower() != "пропустить" else "—"
        await finish_excursion_form(message, state)
        del user_states[uid]

    else:
        del user_states[uid]
        await message.answer(
            "⚠️ Ввод прерван. Попробуйте снова с команды меню.", reply_markup=main_menu
        )


def is_valid_phone(phone: str) -> bool:
    phone = phone.replace(" ", "")
    return re.fullmatch(r"(\+7|8)\d{10}", phone) or re.fullmatch(r"2\d{6}", phone)


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

    await message.answer(
        "✅ Заявка отправлена! Мы скоро с вами свяжемся.", reply_markup=main_menu
    )

    for admin in ADMINS:
        try:
            await message.bot.send_message(admin, msg)
        except Exception:
            pass
