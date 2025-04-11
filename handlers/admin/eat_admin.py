from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu

router = Router()
router.message.filter(IsAdmin())

JSON_PATH = os.path.join(DATA_DIR, "menu.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "меню")


class EditMenu(StatesGroup):
    waiting_for_desc = State()
    choosing_media_action = State()
    deleting_media = State()
    adding_media = State()
    deleting_menu_block = State()


class AddMenu(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


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
    await message.answer("🍽 Управление меню:", reply_markup=keyboard)


@router.message(F.text == "➕ Добавить меню")
async def start_add_menu(message: types.Message, state: FSMContext):
    await state.set_state(AddMenu.waiting_for_desc)
    await message.answer("Введите описание нового блока меню:", reply_markup=back_menu)


@router.message(AddMenu.waiting_for_desc)
async def add_menu_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(AddMenu.waiting_for_media)
    await message.answer(
        "Отправьте медиа (фото/видео), или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(AddMenu.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def add_menu_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media_list = data.get("media", [])
    media_list.append(filename)
    await state.update_data(media=media_list)
    await message.answer("📎 Медиа добавлено. Ещё или напишите 'Готово'")


@router.message(AddMenu.waiting_for_media, F.text.lower() == "готово")
async def finish_add_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    block = {
        "name": "Меню",
        "description": data["desc"],
        "media": data.get("media", []),
    }
    menu = load_json(JSON_PATH)
    if "menu_items" not in menu:
        menu["menu_items"] = []
    menu["menu_items"].append(block)
    save_json(JSON_PATH, menu)
    await state.clear()
    await message.answer("✅ Блок меню добавлен")


@router.message(F.text == "✏️ Изменить меню")
async def edit_menu_desc(message: types.Message, state: FSMContext):
    await state.set_state(EditMenu.waiting_for_desc)
    await message.answer(
        "Введите новое описание для первого блока меню или напишите 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(EditMenu.waiting_for_desc)
async def edit_menu_description(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = load_json(JSON_PATH)
    if data.get("menu_items"):
        if text.lower() != "пропустить":
            data["menu_items"][0]["description"] = text
            save_json(JSON_PATH, data)
    await state.set_state(EditMenu.choosing_media_action)
    await message.answer(
        "Что вы хотите сделать с медиафайлами?",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="➖ Удалить медиа"),
                    types.KeyboardButton(text="➕ Добавить медиа"),
                ],
                [types.KeyboardButton(text="🔚 Завершить")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(EditMenu.choosing_media_action, F.text == "➖ Удалить медиа")
async def delete_existing_media(message: types.Message, state: FSMContext):
    data = load_json(JSON_PATH)
    if not data.get("menu_items") or not data["menu_items"][0].get("media"):
        return await message.answer("Нет медиа для удаления.")

    media_list = data["menu_items"][0]["media"]
    for idx, file in enumerate(media_list, 1):
        full_path = os.path.join(MEDIA_PATH, file)
        if os.path.exists(full_path):
            if file.endswith(".mp4"):
                await message.answer_video(
                    types.FSInputFile(full_path), caption=f"{idx}. {file}"
                )
            else:
                await message.answer_photo(
                    types.FSInputFile(full_path), caption=f"{idx}. {file}"
                )

    await state.set_state(EditMenu.deleting_media)
    await message.answer(
        "Введите номера медиа для удаления через запятую или напишите 'Пропустить':"
    )


@router.message(EditMenu.deleting_media)
async def process_media_deletion(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = load_json(JSON_PATH)
    if text.lower() == "пропустить":
        await state.set_state(EditMenu.choosing_media_action)
        return await message.answer("Ок. Что дальше?", reply_markup=back_menu)

    try:
        indexes = [int(i.strip()) - 1 for i in text.split(",")]
    except ValueError:
        return await message.answer("Некорректный ввод. Введите номера через запятую.")

    media = data["menu_items"][0].get("media", [])
    media_to_keep = []
    for i, file in enumerate(media):
        if i not in indexes:
            media_to_keep.append(file)
        else:
            try:
                os.remove(os.path.join(MEDIA_PATH, file))
            except FileNotFoundError:
                pass

    data["menu_items"][0]["media"] = media_to_keep
    save_json(JSON_PATH, data)
    await state.set_state(EditMenu.choosing_media_action)
    await message.answer(
        "🗑 Указанные медиа удалены. Что дальше?", reply_markup=back_menu
    )


@router.message(EditMenu.choosing_media_action, F.text == "➕ Добавить медиа")
async def start_adding_media(message: types.Message, state: FSMContext):
    await state.set_state(EditMenu.adding_media)
    await message.answer("Отправьте новые фото/видео или напишите 'Готово'")


@router.message(EditMenu.adding_media, F.content_type.in_(["photo", "video"]))
async def add_new_menu_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = load_json(JSON_PATH)
    if data.get("menu_items"):
        data["menu_items"][0].setdefault("media", []).append(filename)
        save_json(JSON_PATH, data)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или 'Готово'")


@router.message(EditMenu.adding_media, F.text.lower() == "готово")
@router.message(EditMenu.choosing_media_action, F.text == "🔚 Завершить")
async def finish_menu_editing(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Меню обновлено")


@router.message(F.text == "🗑 Удалить меню")
async def choose_menu_block_for_deletion(message: types.Message, state: FSMContext):
    data = load_json(JSON_PATH)
    items = data.get("menu_items", [])
    if not items:
        return await message.answer("Меню пока пусто.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["name"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditMenu.deleting_menu_block)
    await message.answer("Выберите блок меню для удаления:", reply_markup=keyboard)


@router.message(EditMenu.deleting_menu_block)
async def delete_menu_block_by_name(message: types.Message, state: FSMContext):
    title = message.text.strip()
    data = load_json(JSON_PATH)
    blocks = data.get("menu_items", [])

    new_blocks = []
    found = False

    for block in blocks:
        if block["name"] == title:
            for file in block.get("media", []):
                try:
                    os.remove(os.path.join(MEDIA_PATH, file))
                except FileNotFoundError:
                    pass
            found = True
        else:
            new_blocks.append(block)

    if not found:
        return await message.answer("❌ Меню с таким названием не найдено.")

    data["menu_items"] = new_blocks
    save_json(JSON_PATH, data)

    await state.clear()
    await message.answer(f"🗑 Блок меню '{title}' удалён.", reply_markup=back_menu)
