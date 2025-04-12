from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .schedule_admin_states import ManageSchedule

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "расписание.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "расписание")


@router.message(ManageSchedule.choosing_action, F.text == "✏️ Изменить расписание")
async def choose_block_to_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    blocks = load_json(JSON_PATH).get(group, [])

    if not blocks:
        return await message.answer("Список пуст")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.update_data(action="edit")
    await state.set_state(ManageSchedule.choosing_block)
    await message.answer("Выберите блок для редактирования:", reply_markup=keyboard)


@router.message(ManageSchedule.choosing_block, F.text.regexp(r"^\d+:"))
async def process_edit_selection(message: types.Message, state: FSMContext):
    index = int(message.text.split(":")[0]) - 1
    data = await state.get_data()
    group = data["group"]
    schedule = load_json(JSON_PATH)

    await state.update_data(block_idx=index, media=[])
    await state.set_state(ManageSchedule.editing_desc)
    await message.answer("Введите новое описание:", reply_markup=back_menu)


@router.message(ManageSchedule.editing_desc)
async def edit_schedule_description(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(ManageSchedule.editing_media)
    await message.answer(
        "Отправьте новые медиа или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(ManageSchedule.editing_media, F.content_type.in_(["photo", "video"]))
async def collect_new_schedule_media(message: types.Message, state: FSMContext):
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


@router.message(ManageSchedule.editing_media, F.text.lower() == "готово")
async def save_edited_schedule(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    idx = data["block_idx"]
    schedule = load_json(JSON_PATH)

    for file in schedule[group][idx].get("media", []):
        try:
            os.remove(os.path.join(MEDIA_PATH, group, file))
        except FileNotFoundError:
            pass

    schedule[group][idx] = {"desc": data["desc"], "media": data.get("media", [])}
    save_json(JSON_PATH, schedule)
    await state.set_state(ManageSchedule.choosing_action)
    await message.answer("✏️ Блок обновлён")
