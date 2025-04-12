from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .announcements_admin_states import DeleteAnnouncement, ManageAnnouncements

router = Router()

SECTION_TITLE = "📰 Анонсы"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageAnnouncements.choosing_action, F.text == "🗑 Удалить анонс")
async def start_delete(message: types.Message, state: FSMContext):
    items = load_json(JSON_PATH)
    if not items:
        return await message.answer("Список анонсов пуст.")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteAnnouncement.waiting_for_selection)
    await message.answer(
        "Выберите анонс для удаления (или 🔙 Назад):", reply_markup=keyboard
    )


@router.message(DeleteAnnouncement.waiting_for_selection)
async def delete_announcement(message: types.Message, state: FSMContext):
    title = message.text.strip()

    if title == "🔙 Назад" or title.lower() == "отмена":
        await state.set_state(ManageAnnouncements.choosing_action)
        return await message.answer("↩️ Возврат в главное меню.", reply_markup=back_menu)

    items = load_json(JSON_PATH)
    new_items = []
    found = False
    for item in items:
        if item["title"] == title:
            for file in item.get("media", []):
                try:
                    os.remove(os.path.join(MEDIA_PATH, file))
                except FileNotFoundError:
                    pass
            found = True
        else:
            new_items.append(item)

    if not found:
        return await message.answer(
            "❌ Анонс не найден. Выберите из списка или '🔙 Назад'."
        )

    save_json(JSON_PATH, new_items)

    # Обновляем список
    items = new_items
    if not items:
        await state.set_state(ManageAnnouncements.choosing_action)
        return await message.answer(
            "🗑 Анонс удалён. Список пуст.", reply_markup=back_menu
        )

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer(
        "🗑 Анонс удалён. Выберите следующий для удаления или '🔙 Назад':",
        reply_markup=keyboard,
    )
