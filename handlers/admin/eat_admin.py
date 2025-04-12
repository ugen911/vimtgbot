# eat_admin.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

# Подроутеры
from .eat_admin_add import router as add_router
from .eat_admin_edit import router as edit_router
from .eat_admin_delete import router as delete_router
from .eat_admin_states import ManageMenu

router = Router()
router.message.filter(IsAdmin())
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)


@router.message(F.text == "/admin_menu")
async def menu_admin_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить меню")],
            [types.KeyboardButton(text="✏️ Изменить меню")],
            [types.KeyboardButton(text="🗑 Удалить меню")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await state.set_state(ManageMenu.choosing_action)
    await message.answer("🍽 Управление меню:", reply_markup=keyboard)
