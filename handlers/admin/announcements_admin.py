from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

router = Router()
router.message.filter(IsAdmin())

SECTION_TITLE = "📰 Анонсы"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


class ManageAnnouncements(StatesGroup):
    choosing_action = State()


class AddAnnouncement(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class DeleteAnnouncement(StatesGroup):
    waiting_for_selection = State()


class EditAnnouncement(StatesGroup):
    waiting_for_choice = State()
    waiting_for_desc = State()
    choosing_media_action = State()
    waiting_for_new_media = State()


@router.message(F.text == "/admin_announcements")
async def admin_announcements_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

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


# Добавление
@router.message(ManageAnnouncements.choosing_action, F.text == "➕ Добавить анонс")
async def start_add_announcement(message: types.Message, state: FSMContext):
    await state.set_state(AddAnnouncement.waiting_for_title)
    await message.answer("Введите заголовок анонса:")


@router.message(AddAnnouncement.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddAnnouncement.waiting_for_desc)
    await message.answer("Введите описание анонса:")


@router.message(AddAnnouncement.waiting_for_desc)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(AddAnnouncement.waiting_for_media)
    await message.answer("Отправьте медиа (фото/видео), или напишите 'Готово'")


@router.message(AddAnnouncement.waiting_for_media, F.text.lower() == "готово")
async def finish_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    items = load_json(JSON_PATH)
    items.append(
        {"title": data["title"], "desc": data["desc"], "media": data.get("media", [])}
    )
    save_json(JSON_PATH, items)
    await state.set_state(ManageAnnouncements.choosing_action)
    await message.answer("✅ Анонс добавлен")


@router.message(
    AddAnnouncement.waiting_for_media, F.content_type.in_(["photo", "video"])
)
async def collect_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")


# Удаление
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
    await message.answer("Выберите анонс для удаления:", reply_markup=keyboard)


@router.message(DeleteAnnouncement.waiting_for_selection)
async def delete_announcement(message: types.Message, state: FSMContext):
    title = message.text.strip()
    items = load_json(JSON_PATH)
    new_items = [item for item in items if item["title"] != title]
    if len(new_items) == len(items):
        return await message.answer("❌ Анонс не найден.")
    save_json(JSON_PATH, new_items)
    await state.set_state(ManageAnnouncements.choosing_action)
    await message.answer("🗑 Анонс удалён")


# Редактирование
@router.message(ManageAnnouncements.choosing_action, F.text == "✏️ Изменить анонс")
async def start_edit(message: types.Message, state: FSMContext):
    items = load_json(JSON_PATH)
    if not items:
        return await message.answer("Список анонсов пуст.")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditAnnouncement.waiting_for_choice)
    await message.answer("Выберите анонс для редактирования:", reply_markup=keyboard)


@router.message(EditAnnouncement.waiting_for_choice)
async def ask_new_desc(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(EditAnnouncement.waiting_for_desc)
    await message.answer("Введите новое описание или напишите 'Пропустить':")


@router.message(EditAnnouncement.waiting_for_desc)
async def maybe_skip_desc(message: types.Message, state: FSMContext):
    if message.text.strip().lower() != "пропустить":
        await state.update_data(desc=message.text.strip())
    await state.set_state(EditAnnouncement.choosing_media_action)
    await message.answer(
        "Удалить старые медиа перед добавлением новых? (Да / Нет / Пропустить)"
    )


@router.message(
    EditAnnouncement.choosing_media_action,
    F.text.lower().in_(["да", "нет", "пропустить"]),
)
async def handle_media_choice(message: types.Message, state: FSMContext):
    answer = message.text.strip().lower()
    if answer == "да":
        await state.update_data(media=[])
    elif answer == "пропустить":
        data = await state.get_data()
        title = data["title"]
        announcements = load_json(JSON_PATH)
        existing = next((item for item in announcements if item["title"] == title), {})
        await state.update_data(media=existing.get("media", []))
    await state.set_state(EditAnnouncement.waiting_for_new_media)
    await message.answer("Отправьте новые медиа или напишите 'Готово'")


@router.message(
    EditAnnouncement.waiting_for_new_media, F.content_type.in_(["photo", "video"])
)
async def collect_edit_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")


@router.message(EditAnnouncement.waiting_for_new_media, F.text.lower() == "готово")
async def finish_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    announcements = load_json(JSON_PATH)
    for item in announcements:
        if item["title"] == title:
            if "desc" in data:
                item["desc"] = data["desc"]
            if "media" in data:
                item["media"] = data["media"]
            break
    save_json(JSON_PATH, announcements)
    await state.set_state(ManageAnnouncements.choosing_action)
    await message.answer("✏️ Анонс обновлён")
