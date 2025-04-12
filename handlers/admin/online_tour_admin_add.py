# online_tour_admin_add.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .online_tour_admin_states import AddTour, ManageTour

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageTour.choosing_action, F.text == "➕ Добавить экскурсию")
async def start_add_tour(message: types.Message, state: FSMContext):
    await state.set_state(AddTour.waiting_for_desc)
    await message.answer("Введите описание экскурсии:", reply_markup=back_menu)


@router.message(AddTour.waiting_for_desc)
async def get_tour_description(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip(), media=[])
    await state.set_state(AddTour.waiting_for_media)
    await message.answer(
        "Отправьте медиафайлы. Когда закончите — напишите 'Готово'",
        reply_markup=back_menu,
    )


@router.message(AddTour.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_tour_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или 'Готово'")


@router.message(AddTour.waiting_for_media, F.text.lower() == "готово")
async def save_new_tour(message: types.Message, state: FSMContext):
    data = await state.get_data()
    blocks = load_json(JSON_PATH)
    blocks.append({"desc": data["desc"], "media": data.get("media", [])})
    save_json(JSON_PATH, blocks)
    await state.clear()
    await message.answer("✅ Экскурсия добавлена")
