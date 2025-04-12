from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import MEDIA_DIR, DATA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .services_admin_states import AddService, ManageService

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageService.choosing_action, F.text == "➕ Добавить услугу")
async def start_add_service(message: types.Message, state: FSMContext):
    await state.set_state(AddService.waiting_for_title)
    await message.answer("Введите заголовок услуги:", reply_markup=back_menu)


@router.message(AddService.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddService.waiting_for_desc)
    await message.answer("Введите описание услуги:", reply_markup=back_menu)


@router.message(AddService.waiting_for_desc)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip(), media=[])
    await state.set_state(AddService.waiting_for_media)
    await message.answer("Отправьте медиафайлы (фото/видео), или напишите 'Готово'")


@router.message(AddService.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")


@router.message(AddService.waiting_for_media, F.text.lower() == "готово")
async def finish_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    items = load_json(JSON_PATH)
    items.append(
        {"title": data["title"], "desc": data["desc"], "media": data.get("media", [])}
    )
    save_json(JSON_PATH, items)
    await state.set_state(ManageService.choosing_action)
    await message.answer("✅ Услуга добавлена")
