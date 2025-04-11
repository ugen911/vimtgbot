from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu, action_menu

router = Router()
router.message.filter(IsAdmin())

JSON_PATH = os.path.join(DATA_DIR, "menu.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "меню")


class EditMenu(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


class AddMenu(StatesGroup):
    waiting_for_desc = State()
    waiting_for_media = State()


@router.message(F.text == "/admin_menu")
async def menu_admin_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")
    await state.clear()
    await message.answer("🍽 Управление меню:", reply_markup=action_menu)


@router.message(F.text == "➕ Добавить")
async def start_add_menu(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current not in [None]:
        return
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
    await message.answer("✅ Блок меню добавлен", reply_markup=action_menu)


@router.message(F.text == "✏️ Изменить")
async def edit_menu_desc(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current not in [None]:
        return
    await state.set_state(EditMenu.waiting_for_desc)
    await message.answer(
        "Введите новое описание для первого блока меню:", reply_markup=back_menu
    )


@router.message(EditMenu.waiting_for_desc)
async def save_menu_desc(message: types.Message, state: FSMContext):
    new_desc = message.text.strip()
    data = load_json(JSON_PATH)

    if data.get("menu_items"):
        data["menu_items"][0]["description"] = new_desc
    else:
        data["menu_items"] = [
            {"name": "Меню дня", "description": new_desc, "media": []}
        ]

    save_json(JSON_PATH, data)
    await state.set_state(EditMenu.waiting_for_media)
    await message.answer(
        "Теперь отправьте новые медиафайлы или напишите 'Готово'",
        reply_markup=back_menu,
    )


@router.message(EditMenu.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_menu_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(
        message.bot, file_id, MEDIA_PATH, is_video=is_video
    )

    data = load_json(JSON_PATH)
    if data.get("menu_items"):
        media = data["menu_items"][0].get("media", [])
        media.append(filename)
        data["menu_items"][0]["media"] = media
        save_json(JSON_PATH, data)

    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(EditMenu.waiting_for_media, F.text.lower() == "готово")
async def finish_edit_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Меню обновлено", reply_markup=action_menu)


@router.message(F.text == "🗑 Удалить")
async def clear_menu_media(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current not in [None]:
        return
    data = load_json(JSON_PATH)
    if data.get("menu_items"):
        data["menu_items"][0]["media"] = []
        save_json(JSON_PATH, data)
        await message.answer(
            "🗑 Все медиафайлы из первого блока меню удалены", reply_markup=action_menu
        )
    else:
        await message.answer("Меню не найдено", reply_markup=action_menu)
