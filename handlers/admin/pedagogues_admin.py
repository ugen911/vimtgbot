from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

from .pedagogues_admin_states import EditPedagogue, ManagePedagogue

# Импорт роутеров из вспомогательных модулей
from .pedagogues_admin_add import router as add_router
from .pedagogues_admin_edit import router as edit_router

router = Router()
router.message.filter(IsAdmin())

# Подключаем вспомогательные роутеры
router.include_router(add_router)
router.include_router(edit_router)

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


@router.message(F.text == "/admin_pedagogues")
async def admin_pedagogues_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👩‍🏫 Воспитатели")],
            [types.KeyboardButton(text="🎓 Преподаватели")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(ManagePedagogue.choosing_role)


@router.message(
    ManagePedagogue.choosing_role, F.text.in_(["👩‍🏫 Воспитатели", "🎓 Преподаватели"])
)
async def ask_action_for_role(message: types.Message, state: FSMContext):
    role = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    await state.update_data(role=role)
    await state.set_state(ManagePedagogue.choosing_action)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить педагога")],
            [types.KeyboardButton(text="✏️ Изменить педагога")],
            [types.KeyboardButton(text="🗑 Удалить педагога")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"Вы выбрали {message.text}. Что хотите сделать?",
        reply_markup=keyboard,
    )
