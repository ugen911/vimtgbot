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
    await state.set_state(ManageSchedule.choosing_block_to_edit)
    await message.answer("Выберите блок для редактирования:", reply_markup=keyboard)


@router.message(ManageSchedule.choosing_block_to_edit, F.text.regexp(r"^\d+:"))
async def process_edit_selection(message: types.Message, state: FSMContext):
    index = int(message.text.split(":")[0]) - 1
    data = await state.get_data()
    group = data["group"]
    schedule = load_json(JSON_PATH)

    await state.update_data(block_idx=index)
    await state.set_state(ManageSchedule.editing_desc)
    await message.answer(
        "Введите новое описание или напишите 'Пропустить':", reply_markup=back_menu
    )


@router.message(ManageSchedule.editing_desc)
async def process_desc(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() != "пропустить":
        await state.update_data(desc=text)

    data = await state.get_data()
    group = data["group"]
    idx = data["block_idx"]
    schedule = load_json(JSON_PATH)
    media = schedule[group][idx].get("media", [])

    if not media:
        await state.update_data(media=[])
        await state.set_state(ManageSchedule.editing_media)
        return await message.answer(
            "Нет медиа. Отправьте новые или 'Готово'", reply_markup=back_menu
        )

    for i, file in enumerate(media, 1):
        full_path = os.path.join(MEDIA_PATH, group, file)
        if os.path.exists(full_path):
            if file.endswith(".mp4"):
                await message.answer_video(
                    types.FSInputFile(full_path), caption=f"{i}. {file}"
                )
            else:
                await message.answer_photo(
                    types.FSInputFile(full_path), caption=f"{i}. {file}"
                )

    await state.update_data(media=media)
    await state.set_state(ManageSchedule.deleting_media)
    await message.answer(
        "Введите номера медиа для удаления через запятую или 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(ManageSchedule.deleting_media)
async def delete_selected_media(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()

    if text == "пропустить":
        await state.set_state(ManageSchedule.editing_media)
        return await message.answer(
            "Ок. Отправьте новые медиа или 'Готово'", reply_markup=back_menu
        )

    if text == "отмена":
        await state.clear()
        return await message.answer("❌ Действие отменено", reply_markup=back_menu)

    try:
        indexes = [int(i.strip()) - 1 for i in text.split(",")]
    except ValueError:
        return await message.answer(
            "❌ Неверный формат. Введите номера через запятую, например: 1, 2"
        )

    data = await state.get_data()
    group = data["group"]
    idx = data["block_idx"]
    schedule = load_json(JSON_PATH)

    current_media = data.get("media", [])
    new_media = []

    for i, file in enumerate(current_media):
        if i not in indexes:
            new_media.append(file)
        else:
            try:
                os.remove(os.path.join(MEDIA_PATH, group, file))
            except FileNotFoundError:
                pass

    await state.update_data(media=new_media)
    await state.set_state(ManageSchedule.editing_media)
    await message.answer(
        "🗑 Медиа удалены. Отправьте новые или 'Готово'", reply_markup=back_menu
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

    if "desc" in data:
        schedule[group][idx]["desc"] = data["desc"]
    if "media" in data:
        schedule[group][idx]["media"] = data["media"]

    save_json(JSON_PATH, schedule)
    await state.set_state(ManageSchedule.choosing_action)
    await message.answer("✏️ Блок расписания обновлён")
