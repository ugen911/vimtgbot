from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
import json
from config import DATA_DIR, ADMINS as PERMANENT_ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

router = Router()
router.message.filter(IsAdmin())

ADMINS_PATH = os.path.join(DATA_DIR, "admins.json")


class ManageAdmins(StatesGroup):
    waiting_for_add = State()
    waiting_for_remove = State()


def load_dynamic_admins():
    if not os.path.exists(ADMINS_PATH):
        return []
    with open(ADMINS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dynamic_admins(admins):
    with open(ADMINS_PATH, "w", encoding="utf-8") as f:
        json.dump(admins, f, indent=2)


def is_permanent(admin_id_or_username: str) -> bool:
    return str(admin_id_or_username) in map(str, PERMANENT_ADMINS)


@router.message(F.text == "⚙️ Админы")
async def show_admin_menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👥 Список администраторов")],
            [
                types.KeyboardButton(text="➕ Добавить администратора"),
                types.KeyboardButton(text="➕ Я"),
            ],
            [types.KeyboardButton(text="🗑 Удалить администратора")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await state.clear()
    await message.answer("Выберите действие:", reply_markup=keyboard)


@router.message(F.text == "👥 Список администраторов")
async def list_admins(message: types.Message):
    dynamic_admins = load_dynamic_admins()
    all_admins = list(
        dict.fromkeys([*PERMANENT_ADMINS, *dynamic_admins])
    )  # remove duplicates, keep order
    text = "\n".join(
        f"• <code>{admin}</code>{' (постоянный)' if str(admin) in map(str, PERMANENT_ADMINS) else ''}"
        for admin in all_admins
    )
    await message.answer(
        f"<b>Список администраторов:</b>\n{text or 'Нет админов.'}", parse_mode="HTML"
    )


@router.message(F.text == "➕ Добавить администратора")
async def start_add_admin(message: types.Message, state: FSMContext):
    await state.set_state(ManageAdmins.waiting_for_add)
    await message.answer(
        "Введите ID или @username для добавления администратора:",
        reply_markup=back_menu,
    )


@router.message(ManageAdmins.waiting_for_add)
async def handle_add_admin(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    all_admins = list(map(str, PERMANENT_ADMINS)) + load_dynamic_admins()

    if raw in all_admins:
        return await message.answer("⚠️ Этот пользователь уже в списке администраторов.")

    dynamic_admins = load_dynamic_admins()
    dynamic_admins.append(raw)
    save_dynamic_admins(dynamic_admins)
    await state.clear()
    await message.answer(
        f"✅ <code>{raw}</code> добавлен в администраторы.", parse_mode="HTML"
    )


@router.message(F.text == "🗑 Удалить администратора")
async def start_remove_admin(message: types.Message, state: FSMContext):
    await state.set_state(ManageAdmins.waiting_for_remove)
    await message.answer(
        "Введите ID или @username для удаления администратора:", reply_markup=back_menu
    )


@router.message(ManageAdmins.waiting_for_remove)
async def handle_remove_admin(message: types.Message, state: FSMContext):
    raw = message.text.strip()
    user_id = str(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else None

    if raw in (user_id, username):
        return await message.answer("❌ Вы не можете удалить самого себя.")

    if is_permanent(raw):
        return await message.answer(
            "⛔ Нельзя удалить постоянного администратора (из config.py)."
        )

    dynamic_admins = load_dynamic_admins()
    if raw not in dynamic_admins:
        return await message.answer("❌ Этот администратор не найден в списке.")

    dynamic_admins.remove(raw)
    save_dynamic_admins(dynamic_admins)
    await state.clear()
    await message.answer(
        f"🗑 <code>{raw}</code> удалён из списка администраторов.", parse_mode="HTML"
    )


@router.message(F.text == "➕ Я")
async def add_self_to_admins(message: types.Message):
    user_id = str(message.from_user.id)
    dynamic_admins = load_dynamic_admins()
    if user_id in dynamic_admins or user_id in map(str, PERMANENT_ADMINS):
        return await message.answer("⚠️ Вы уже в списке администраторов.")

    dynamic_admins.append(user_id)
    save_dynamic_admins(dynamic_admins)
    await message.answer(
        f"✅ Вы добавлены как <code>{user_id}</code>", parse_mode="HTML"
    )
