from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS, ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

# Импорт подроутеров
from .announcements_admin_add import router as add_router
from .announcements_admin_edit import router as edit_router
from .announcements_admin_delete import router as delete_router
from .announcements_admin_states import ManageAnnouncements  # ← только импорт

router = Router()
router.message.filter(IsAdmin())
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)

SECTION_TITLE = "📰 Анонсы"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(F.text == "/admin_announcements")
async def admin_announcements_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить анонс")],
            [types.KeyboardButton(text="✏️ Изменить анонс")],
            [types.KeyboardButton(text="🗑 Удалить анонс")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await state.set_state(ManageAnnouncements.choosing_action)
    await message.answer("📢 Управление анонсами:", reply_markup=keyboard)
