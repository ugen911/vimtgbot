from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .schedule_admin_states import EditSchedule, ManageSchedule

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "расписание.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "расписание")


@router.message(ManageSchedule.choosing_action, F.text == "➕ Добавить расписание")
async def start_adding_schedule(message: types.Message, state: FSMContext):
    await state.set_state(EditSchedule.entering_desc)
    await message.answer("Введите описание блока:", reply_markup=back_menu)


@router.message(EditSchedule.entering_desc)
async def input_schedule_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip(), media=[])
    await state.set_state(EditSchedule.entering_media)
    await message.answer(
        "Отправьте медиа или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(EditSchedule.entering_media, F.content_type.in_(["photo", "video"]))
async def collect_schedule_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    group_path = os.path.join(MEDIA_PATH, group)
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, group_path, is_video)
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(EditSchedule.entering_media, F.text.lower() == "готово")
async def finish_add_schedule(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    schedule = load_json(JSON_PATH)
    schedule.setdefault(group, []).append(
        {"desc": data["desc"], "media": data.get("media", [])}
    )
    save_json(JSON_PATH, schedule)
    await state.set_state(ManageSchedule.choosing_action)
    await message.answer("✅ Блок добавлен")
