# online_tour_admin.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS, ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

# Импорт подроутеров
from .online_tour_admin_add import router as add_router
from .online_tour_admin_edit import router as edit_router
from .online_tour_admin_delete import router as delete_router
from .online_tour_admin_states import ManageTour

router = Router()
router.message.filter(IsAdmin())
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(F.text == "/admin_online")
async def admin_online_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить экскурсию")],
            [types.KeyboardButton(text="✏️ Изменить экскурсию")],
            [types.KeyboardButton(text="🗑 Удалить экскурсию")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await state.set_state(ManageTour.choosing_action)
    await message.answer("🌐 Управление онлайн-экскурсиями:", reply_markup=keyboard)
