from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .pedagogues_admin_states import ManagePedagogue

import os

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


@router.message(
    ManagePedagogue.choosing_action,
    F.text.in_(["✏️ Изменить педагога", "🗑 Удалить педагога"]),
)
async def choose_pedagogue_for_edit_or_delete(
    message: types.Message, state: FSMContext
):
    action = message.text
    data = await state.get_data()
    role = data["role"]
    await state.update_data(action=action)
    all_data = load_json(JSON_PATH)
    names = [p["name"] for p in all_data.get(role, [])]

    if not names:
        return await message.answer("Список пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=name)] for name in names]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManagePedagogue.choosing_name)
    await message.answer("Выберите имя:", reply_markup=keyboard)


@router.message(ManagePedagogue.choosing_name)
async def handle_pedagogue_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]
    name = message.text.strip()
    all_data = load_json(JSON_PATH)
    index = next((i for i, p in enumerate(all_data[role]) if p["name"] == name), -1)

    if index == -1:
        return await message.answer("❌ Не найдено")

    await state.update_data(name=name, index=index)

    if data["action"] == "🗑 Удалить педагога":
        for file in all_data[role][index].get("media", []):
            try:
                os.remove(os.path.join(MEDIA_PATH, role, file))
            except FileNotFoundError:
                pass
        del all_data[role][index]
        save_json(JSON_PATH, all_data)
        await state.set_state(ManagePedagogue.choosing_action)
        return await message.answer("🗑 Удалено")

    await message.answer(
        "Введите новое имя или напишите 'Пропустить':", reply_markup=back_menu
    )
    await state.set_state(ManagePedagogue.editing_name)


@router.message(ManagePedagogue.editing_name)
async def edit_name(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() != "пропустить":
        await state.update_data(new_name=text)
    await message.answer(
        "Введите новую роль или напишите 'Пропустить':", reply_markup=back_menu
    )
    await state.set_state(ManagePedagogue.editing_role)


@router.message(ManagePedagogue.editing_role)
async def edit_role(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() != "пропустить":
        await state.update_data(new_role=text)
    await message.answer(
        "Введите новое описание или напишите 'Пропустить':", reply_markup=back_menu
    )
    await state.set_state(ManagePedagogue.editing_description)


@router.message(ManagePedagogue.editing_description)
async def edit_description(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()
    if text.lower() != "пропустить":
        await state.update_data(description=text)
    data = await state.get_data()
    all_data = load_json(JSON_PATH)
    current_media = all_data[data["role"]][data["index"]].get("media", [])

    if not current_media:
        await state.update_data(media=[])
        await message.answer(
            "Нет медиа. Отправьте новые или 'Готово'", reply_markup=back_menu
        )
        return await state.set_state(ManagePedagogue.editing_media)

    for idx, file in enumerate(current_media, 1):
        file_path = os.path.join(MEDIA_PATH, data["role"], file)
        if os.path.exists(file_path):
            if file.endswith(".mp4"):
                await message.answer_video(
                    FSInputFile(file_path), caption=f"{idx}. {file}"
                )
            else:
                await message.answer_photo(
                    FSInputFile(file_path), caption=f"{idx}. {file}"
                )

    await state.set_state(ManagePedagogue.deleting_media)
    await message.answer(
        "Введите номера медиа для удаления через запятую или напишите 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(ManagePedagogue.deleting_media)
async def delete_selected_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_data = load_json(JSON_PATH)
    media = all_data[data["role"]][data["index"]].get("media", [])

    if (message.text or "").strip().lower() == "пропустить":
        await state.update_data(media=media)
        await state.set_state(ManagePedagogue.editing_media)
        return await message.answer(
            "Хорошо. Отправьте новые медиа или 'Готово'", reply_markup=back_menu
        )

    try:
        indexes = [int(i.strip()) - 1 for i in message.text.split(",")]
    except ValueError:
        return await message.answer(
            "Некорректный формат. Введите номера через запятую."
        )

    new_media = []
    for i, file in enumerate(media):
        if i not in indexes:
            new_media.append(file)
        else:
            try:
                os.remove(os.path.join(MEDIA_PATH, data["role"], file))
            except FileNotFoundError:
                pass

    await state.update_data(media=new_media)
    await state.set_state(ManagePedagogue.editing_media)
    await message.answer(
        "🗑 Указанные медиа удалены. Отправьте новые или 'Готово'",
        reply_markup=back_menu,
    )


@router.message(ManagePedagogue.editing_media, F.content_type.in_(["photo", "video"]))
async def collect_edit_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    data = await state.get_data()
    media_path = os.path.join(MEDIA_PATH, data["role"])
    filename = await save_media_file(
        message.bot, file_id, media_path, is_video=is_video
    )
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(ManagePedagogue.editing_media, F.text.lower() == "готово")
async def finish_editing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_data = load_json(JSON_PATH)
    record = all_data[data["role"]][data["index"]]

    if "new_name" in data:
        record["name"] = data["new_name"]
    if "new_role" in data:
        record["role"] = data["new_role"]
    if "description" in data:
        record["description"] = data["description"]
    if "media" in data:
        record["media"] = data["media"]

    save_json(JSON_PATH, all_data)
    await state.set_state(ManagePedagogue.choosing_action)
    await message.answer("✏️ Данные педагога обновлены")
