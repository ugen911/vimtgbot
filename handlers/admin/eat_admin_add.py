from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .eat_admin_states import AddMenu, ManageMenu

router = Router()

SECTION_TITLE = "🍽 Меню"
SECTION_KEY = "menu"
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageMenu.choosing_action, F.text == "➕ Добавить меню")
async def start_add_menu(message: types.Message, state: FSMContext):
    await state.set_state(AddMenu.waiting_for_desc)
    await message.answer("Введите описание нового блока меню:", reply_markup=back_menu)


@router.message(AddMenu.waiting_for_desc)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip(), media=[])
    await state.set_state(AddMenu.waiting_for_media)
    await message.answer("Отправьте медиа (фото/видео), или напишите 'Готово'")


@router.message(AddMenu.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    media = (await state.get_data()).get("media", [])
    media.append(filename)
    await state.update_data(media=media)
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

    # 🛡️ Защита от повреждённого menu.json
    if isinstance(menu, list):
        menu = {"menu_items": menu}
    elif not isinstance(menu, dict):
        menu = {"menu_items": []}

    if "menu_items" not in menu:
        menu["menu_items"] = []
    menu["menu_items"].append(block)

    save_json(JSON_PATH, menu)
    await state.set_state(ManageMenu.choosing_action)
    await message.answer("✅ Блок меню добавлен")
