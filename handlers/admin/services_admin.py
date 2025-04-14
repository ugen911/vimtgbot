from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from config import ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu
from .services_admin_states import ManageService

# Подключаем подмодули
from .services_admin_add import router as add_router
from .services_admin_edit import router as edit_router
from .services_admin_delete import router as delete_router


router = Router()
router.message.filter(IsAdmin())

# Подключение подмодулей
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)


@router.message(F.text == "/admin_services")
async def admin_services_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить услугу")],
            [types.KeyboardButton(text="✏️ Изменить услугу")],
            [types.KeyboardButton(text="🗑 Удалить услугу")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await state.set_state(ManageService.choosing_action)
    await message.answer("🔧 Управление услугами:", reply_markup=keyboard)
