from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())

SECTION_TITLE = "📰 Анонсы"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


class AddAnnouncement(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class DeleteAnnouncement(StatesGroup):
    waiting_for_selection = State()


class EditAnnouncement(StatesGroup):
    waiting_for_announcement_choice = State()
    waiting_for_new_desc = State()
    waiting_for_new_media = State()


@router.message(F.text == "/admin_announcements")
async def admin_announcements_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await message.answer(
        "📢 Управление анонсами:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="➕ Добавить анонс")],
                [types.KeyboardButton(text="🗑 Удалить анонс")],
                [types.KeyboardButton(text="✏️ Изменить анонс")],
                [types.KeyboardButton(text="🔙 Назад")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(F.text == "➕ Добавить анонс")
async def start_add_announcement(message: types.Message, state: FSMContext):
    await state.set_state(AddAnnouncement.waiting_for_title)
    await message.answer("Введите заголовок анонса:")


@router.message(AddAnnouncement.waiting_for_title)
async def process_announcement_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddAnnouncement.waiting_for_desc)
    await message.answer("Введите описание анонса:")


@router.message(AddAnnouncement.waiting_for_desc)
async def process_announcement_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(AddAnnouncement.waiting_for_media)
    await message.answer(
        "Отправьте медиафайлы (фото/видео). Когда закончите — напишите 'Готово'"
    )


@router.message(AddAnnouncement.waiting_for_media, F.text.lower() == "готово")
async def finish_add_announcement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    desc = data["desc"]
    media = data.get("media", [])

    items = load_json(JSON_PATH)
    items.append({"title": title, "desc": desc, "media": media})
    save_json(JSON_PATH, items)

    await state.clear()
    await message.answer("✅ Анонс добавлен")


@router.message(
    AddAnnouncement.waiting_for_media, F.content_type.in_(["photo", "video"])
)
async def collect_announcement_media(message: types.Message, state: FSMContext):
    media_list = []
    if message.photo:
        file_id = message.photo[-1].file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=False
        )
        media_list.append(filename)
    elif message.video:
        file_id = message.video.file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=True
        )
        media_list.append(filename)

    state_data = await state.get_data()
    all_media = state_data.get("media", []) + media_list
    await state.update_data(media=all_media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")


@router.message(F.text == "🗑 Удалить анонс")
async def start_delete_announcement(message: types.Message, state: FSMContext):
    items = load_json(JSON_PATH)
    if not items:
        return await message.answer("Список анонсов пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteAnnouncement.waiting_for_selection)
    await message.answer("Выберите анонс для удаления:", reply_markup=keyboard)


@router.message(DeleteAnnouncement.waiting_for_selection)
async def process_delete_announcement(message: types.Message, state: FSMContext):
    title_to_delete = message.text.strip()
    items = load_json(JSON_PATH)

    new_items = [item for item in items if item["title"] != title_to_delete]
    if len(new_items) == len(items):
        return await message.answer("❌ Анонс не найден.")

    save_json(JSON_PATH, new_items)
    await state.clear()
    await message.answer("🗑 Анонс удалён.")


@router.message(F.text == "✏️ Изменить анонс")
async def start_edit_announcement(message: types.Message, state: FSMContext):
    items = load_json(JSON_PATH)
    if not items:
        return await message.answer("Список анонсов пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditAnnouncement.waiting_for_announcement_choice)
    await message.answer("Выберите анонс для редактирования:", reply_markup=keyboard)


@router.message(EditAnnouncement.waiting_for_announcement_choice)
async def ask_announcement_new_desc(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(EditAnnouncement.waiting_for_new_desc)
    await message.answer("Введите новое описание:")


@router.message(EditAnnouncement.waiting_for_new_desc)
async def ask_announcement_new_media(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(EditAnnouncement.waiting_for_new_media)
    await message.answer("Отправьте новые медиафайлы или напишите 'Готово':")


@router.message(EditAnnouncement.waiting_for_new_media, F.text.lower() == "готово")
async def save_edited_announcement(message: types.Message, state: FSMContext):
    data = await state.get_data()
    items = load_json(JSON_PATH)

    for item in items:
        if item["title"] == data["title"]:
            item["desc"] = data["desc"]
            item["media"] = data.get("media", [])
            break

    save_json(JSON_PATH, items)
    await state.clear()
    await message.answer("✏️ Анонс обновлён.")


@router.message(
    EditAnnouncement.waiting_for_new_media, F.content_type.in_(["photo", "video"])
)
async def collect_announcement_new_media(message: types.Message, state: FSMContext):
    media_list = []
    if message.photo:
        file_id = message.photo[-1].file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=False
        )
        media_list.append(filename)
    elif message.video:
        file_id = message.video.file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=True
        )
        media_list.append(filename)

    state_data = await state.get_data()
    all_media = state_data.get("media", []) + media_list
    await state.update_data(media=all_media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")
