from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .eat_admin_states import EditMenu, ManageMenu

router = Router()

SECTION_TITLE = "🍽 Меню"
SECTION_KEY = "menu"
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageMenu.choosing_action, F.text == "✏️ Изменить меню")
async def start_edit_menu(message: types.Message, state: FSMContext):
    data = load_json(JSON_PATH)

    # 🛡️ Защита
    if isinstance(data, list):
        data = {"menu_items": data}
    elif not isinstance(data, dict):
        data = {"menu_items": []}

    items = data.get("menu_items", [])
    if not items:
        return await message.answer("Список меню пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["description"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditMenu.waiting_for_choice)
    await message.answer("Выберите блок меню по описанию:", reply_markup=keyboard)


@router.message(EditMenu.waiting_for_choice)
async def ask_new_description(message: types.Message, state: FSMContext):
    await state.update_data(old_desc=message.text.strip())
    await state.set_state(EditMenu.editing_desc)
    await message.answer(
        "Введите новое описание или напишите 'Пропустить':", reply_markup=back_menu
    )


@router.message(EditMenu.editing_desc)
async def process_new_description(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() != "пропустить":
        await state.update_data(new_desc=text)

    data = await state.get_data()
    menu = load_json(JSON_PATH)

    # 🛡️ Защита
    if isinstance(menu, list):
        menu = {"menu_items": menu}
    elif not isinstance(menu, dict):
        menu = {"menu_items": []}

    item = next(
        (x for x in menu.get("menu_items", []) if x["description"] == data["old_desc"]),
        None,
    )
    if not item:
        return await message.answer("❌ Блок меню не найден")

    media = item.get("media", [])
    await state.update_data(media=media)

    for idx, file in enumerate(media, 1):
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
        "Введите номера медиа для удаления через запятую или 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(EditMenu.deleting_media)
async def delete_selected_media(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text == "пропустить":
        await state.set_state(EditMenu.adding_media)
        return await message.answer(
            "Ок. Теперь отправьте новые медиа или 'Готово'", reply_markup=back_menu
        )

    if text == "отмена":
        await state.clear()
        return await message.answer(
            "❌ Действие отменено. Возвращаюсь в меню.", reply_markup=back_menu
        )

    try:
        indexes = [int(i.strip()) - 1 for i in text.split(",")]
    except ValueError:
        return await message.answer(
            "❌ Неверный формат. Введите номера через запятую, например: `1, 2`.\n"
            "Или напишите <b>отмена</b>, чтобы выйти в главное меню.",
            parse_mode="HTML",
        )

    data = await state.get_data()
    current_media = data.get("media", [])
    new_media = []

    for i, file in enumerate(current_media):
        if i not in indexes:
            new_media.append(file)
        else:
            try:
                os.remove(os.path.join(MEDIA_PATH, file))
            except FileNotFoundError:
                pass

    await state.update_data(media=new_media)
    await state.set_state(EditMenu.adding_media)
    await message.answer(
        "🗑 Медиа удалены. Отправьте новые или 'Готово'", reply_markup=back_menu
    )


@router.message(EditMenu.adding_media, F.content_type.in_(["photo", "video"]))
async def collect_new_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(EditMenu.adding_media, F.text.lower() == "готово")
async def save_menu_changes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu = load_json(JSON_PATH)

    # 🛡️ Защита
    if isinstance(menu, list):
        menu = {"menu_items": menu}
    elif not isinstance(menu, dict):
        menu = {"menu_items": []}

    updated = False
    for item in menu.get("menu_items", []):
        if item["description"] == data["old_desc"]:
            if "new_desc" in data:
                item["description"] = data["new_desc"]
            item["media"] = data.get("media", [])
            updated = True
            break

    if updated:
        save_json(JSON_PATH, menu)
        await message.answer("✅ Меню обновлено")
    else:
        await message.answer("❌ Не удалось сохранить изменения")

    await state.set_state(ManageMenu.choosing_action)
