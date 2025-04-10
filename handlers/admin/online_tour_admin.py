from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin

router = Router()
router.message.filter(IsAdmin())

SECTION_KEY = "онлайнэкскурсии"
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


class AddTour(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


class EditTour(StatesGroup):
    waiting_for_selection = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class DeleteTour(StatesGroup):
    waiting_for_selection = State()


@router.message(F.text == "/admin_online")
async def admin_online_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await message.answer(
        "🌐 Управление онлайн-экскурсиями:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="➕ Добавить блок")],
                [
                    types.KeyboardButton(text="✏️ Изменить блок"),
                    types.KeyboardButton(text="🗑 Удалить блок"),
                ],
                [types.KeyboardButton(text="🔙 В админ-панель")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(F.text == "🔙 В админ-панель")
async def back_to_admin_panel(message: types.Message):
    await message.bot.send_message(message.chat.id, "/admin")


@router.message(F.text == "➕ Добавить блок")
async def start_add_tour(message: types.Message, state: FSMContext):
    await state.set_state(AddTour.waiting_for_desc)
    await message.answer("Введите описание блока:")


@router.message(AddTour.waiting_for_desc)
async def get_tour_description(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(AddTour.waiting_for_media)
    await message.answer("Отправьте медиафайлы. Когда закончите — напишите 'Готово'")


@router.message(AddTour.waiting_for_media, F.text.lower() == "готово")
async def save_new_tour(message: types.Message, state: FSMContext):
    data = await state.get_data()
    desc = data["desc"]
    media = data.get("media", [])
    blocks = load_json(JSON_PATH)
    blocks.append({"desc": desc, "media": media})
    save_json(JSON_PATH, blocks)
    await state.clear()
    await message.answer("✅ Блок добавлен")


@router.message(AddTour.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_tour_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    media = (await state.get_data()).get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или 'Готово'")


@router.message(F.text == "🗑 Удалить блок")
async def start_delete_tour(message: types.Message, state: FSMContext):
    blocks = load_json(JSON_PATH)
    if not blocks:
        return await message.answer("Список пуст")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ],
        resize_keyboard=True,
    )
    await state.set_state(DeleteTour.waiting_for_selection)
    await message.answer("Выберите блок для удаления:", reply_markup=keyboard)


@router.message(DeleteTour.waiting_for_selection, F.text.regexp(r"^\d+:"))
async def delete_selected_tour(message: types.Message, state: FSMContext):
    idx = int(message.text.split(":")[0]) - 1
    blocks = load_json(JSON_PATH)
    if 0 <= idx < len(blocks):
        del blocks[idx]
        save_json(JSON_PATH, blocks)
        await message.answer("🗑 Блок удалён")
    await state.clear()


@router.message(F.text == "✏️ Изменить блок")
async def start_edit_tour(message: types.Message, state: FSMContext):
    blocks = load_json(JSON_PATH)
    if not blocks:
        return await message.answer("Список пуст")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ],
        resize_keyboard=True,
    )
    await state.set_state(EditTour.waiting_for_selection)
    await message.answer("Выберите блок для редактирования:", reply_markup=keyboard)


@router.message(EditTour.waiting_for_selection, F.text.regexp(r"^\d+:"))
async def edit_tour_desc(message: types.Message, state: FSMContext):
    idx = int(message.text.split(":")[0]) - 1
    await state.update_data(index=idx)
    await state.set_state(EditTour.waiting_for_desc)
    await message.answer("Введите новое описание:")


@router.message(EditTour.waiting_for_desc)
async def edit_tour_media_prompt(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(EditTour.waiting_for_media)
    await message.answer("Отправьте новые медиа или 'Готово'")


@router.message(EditTour.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_edit_tour_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    media = (await state.get_data()).get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или 'Готово'")


@router.message(EditTour.waiting_for_media, F.text.lower() == "готово")
async def save_edited_tour(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data["index"]
    blocks = load_json(JSON_PATH)
    if 0 <= idx < len(blocks):
        blocks[idx] = {"desc": data["desc"], "media": data.get("media", [])}
        save_json(JSON_PATH, blocks)
        await message.answer("✏️ Блок обновлён")
    await state.clear()
