# online_tour_admin_edit.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .online_tour_admin_states import EditTour, ManageTour

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageTour.choosing_action, F.text == "✏️ Изменить экскурсию")
async def start_edit_tour(message: types.Message, state: FSMContext):
    blocks = load_json(JSON_PATH)
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
    await state.set_state(EditTour.waiting_for_selection)
    await message.answer(
        "Выберите экскурсию для редактирования:", reply_markup=keyboard
    )


@router.message(EditTour.waiting_for_selection, F.text.regexp(r"^\d+:"))
async def edit_tour_desc(message: types.Message, state: FSMContext):
    idx = int(message.text.split(":")[0]) - 1
    blocks = load_json(JSON_PATH)

    if not (0 <= idx < len(blocks)):
        return await message.answer("❌ Неверный выбор.")

    await state.update_data(index=idx)
    await state.set_state(EditTour.waiting_for_desc)
    await message.answer(
        "Введите новое описание или 'Пропустить':", reply_markup=back_menu
    )


@router.message(EditTour.waiting_for_desc)
async def preview_and_prompt_delete_media(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() != "пропустить":
        await state.update_data(desc=text)

    data = await state.get_data()
    blocks = load_json(JSON_PATH)
    idx = data["index"]
    media_list = blocks[idx].get("media", [])

    if not media_list:
        await state.set_state(EditTour.waiting_for_media)
        return await message.answer(
            "Нет текущих медиа. Отправьте новые или 'Готово'", reply_markup=back_menu
        )

    await state.set_state(EditTour.deleting_media)
    for i, file in enumerate(media_list, 1):
        path = os.path.join(MEDIA_PATH, file)
        if os.path.exists(path):
            if file.endswith(".mp4"):
                await message.answer_video(FSInputFile(path), caption=f"{i}. {file}")
            else:
                await message.answer_photo(FSInputFile(path), caption=f"{i}. {file}")
    await message.answer(
        "Введите номера медиа для удаления через запятую или напишите 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(EditTour.deleting_media)
async def delete_selected_media(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    idx = data["index"]
    blocks = load_json(JSON_PATH)
    media = blocks[idx].get("media", [])

    if text.lower() == "пропустить":
        await state.set_state(EditTour.waiting_for_media)
        return await message.answer(
            "Ок. Отправьте новые медиа или 'Готово'", reply_markup=back_menu
        )

    try:
        indexes = [int(i.strip()) - 1 for i in text.split(",")]
    except ValueError:
        return await message.answer(
            "❌ Некорректный ввод. Введите номера через запятую."
        )

    new_media = []
    for i, file in enumerate(media):
        if i not in indexes:
            new_media.append(file)
        else:
            try:
                os.remove(os.path.join(MEDIA_PATH, file))
            except FileNotFoundError:
                pass

    blocks[idx]["media"] = new_media
    save_json(JSON_PATH, blocks)
    await state.set_state(EditTour.waiting_for_media)
    await message.answer(
        "🗑 Указанные медиа удалены. Отправьте новые или 'Готово'",
        reply_markup=back_menu,
    )


@router.message(EditTour.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_edit_tour_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)

    data = await state.get_data()
    idx = data["index"]
    blocks = load_json(JSON_PATH)
    blocks[idx].setdefault("media", []).append(filename)
    save_json(JSON_PATH, blocks)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или 'Готово'")


@router.message(EditTour.waiting_for_media, F.text.lower() == "готово")
async def save_edited_tour(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data["index"]
    blocks = load_json(JSON_PATH)
    if "desc" in data:
        blocks[idx]["desc"] = data["desc"]
    save_json(JSON_PATH, blocks)
    await state.clear()
    await message.answer("✏️ Экскурсия обновлена")
