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


def delete_media_files(filenames: list[str]):
    deleted = 0
    for file in filenames:
        path = os.path.join(MEDIA_PATH, file)
        if os.path.exists(path):
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении {path}: {e}")
        else:
            print(f"[WARNING] Файл не найден: {path}")
    print(f"[INFO] Удалено файлов: {deleted}")


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
            delete_media_files(item.get("media", []))
            found = True
        else:
            new_items.append(item)

    if not found:
        return await message.answer(
            "❌ Анонс не найден. Выберите из списка или '🔙 Назад'."
        )

    save_json(JSON_PATH, new_items)

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
