from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .services_admin_states import EditService, ManageService, DeleteService

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageService.choosing_action, F.text == "✏️ Изменить услугу")
async def start_edit_service(message: types.Message, state: FSMContext):
    services = load_json(JSON_PATH)
    if not services:
        return await message.answer("Список услуг пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditService.waiting_for_choice)
    await message.answer("Выберите услугу для редактирования:", reply_markup=keyboard)


@router.message(ManageService.choosing_action, F.text == "🗑 Удалить услугу")
async def start_delete_service(message: types.Message, state: FSMContext):
    services = load_json(JSON_PATH)
    if not services:
        return await message.answer("Список услуг пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteService.waiting_for_selection)
    await message.answer("Выберите услугу для удаления:", reply_markup=keyboard)


@router.message(DeleteService.waiting_for_selection)
async def delete_service_by_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    services = load_json(JSON_PATH)
    new_services = []
    found = False

    for svc in services:
        if svc["title"] == title:
            for file in svc.get("media", []):
                try:
                    os.remove(os.path.join(MEDIA_PATH, file))
                except FileNotFoundError:
                    pass
            found = True
        else:
            new_services.append(svc)

    if not found:
        return await message.answer("❌ Услуга не найдена")

    save_json(JSON_PATH, new_services)
    await message.answer("🗑 Услуга удалена")

    # Предложим удалить ещё одну
    services = new_services
    if not services:
        await state.set_state(ManageService.choosing_action)
        return await message.answer("Список услуг теперь пуст.", reply_markup=back_menu)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["title"])] for item in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer("Хотите удалить ещё одну? Выберите:", reply_markup=keyboard)


@router.message(EditService.waiting_for_choice)
async def ask_new_description(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(EditService.editing_desc)
    await message.answer(
        "Введите новое описание или напишите 'Пропустить':", reply_markup=back_menu
    )


@router.message(EditService.editing_desc)
async def process_new_description(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() != "пропустить":
        await state.update_data(desc=text)

    services = load_json(JSON_PATH)
    data = await state.get_data()
    service = next((s for s in services if s["title"] == data["title"]), None)
    if not service:
        return await message.answer("❌ Услуга не найдена")

    media = service.get("media", [])
    if not media:
        await state.update_data(media=[])
        await state.set_state(EditService.adding_media)
        return await message.answer(
            "Нет медиа. Отправьте новые или 'Готово'", reply_markup=back_menu
        )

    # Превью медиа
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

    await state.update_data(media=media)
    await state.set_state(EditService.deleting_media)
    await message.answer(
        "Введите номера медиа для удаления (через запятую), или 'Пропустить', или 'Отменить':",
        reply_markup=back_menu,
    )


@router.message(EditService.deleting_media)
async def delete_selected_media(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    data = await state.get_data()
    current_media = data.get("media", [])

    if text == "пропустить":
        await state.set_state(EditService.adding_media)
        return await message.answer(
            "Ок. Теперь отправьте новые медиа или 'Готово'", reply_markup=back_menu
        )

    if text == "отменить":
        await state.clear()
        return await message.answer("❌ Действие отменено", reply_markup=back_menu)

    try:
        indexes = [int(i.strip()) - 1 for i in text.split(",")]
        if any(i < 0 or i >= len(current_media) for i in indexes):
            raise IndexError
    except (ValueError, IndexError):
        return await message.answer(
            "❌ Неверный ввод. Введите номера через запятую. Пример: 1, 3"
        )

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

    # Повторно показать список для новой итерации
    if new_media:
        for idx, file in enumerate(new_media, 1):
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

        await message.answer(
            "Удалить ещё? Введите номера или 'Пропустить':", reply_markup=back_menu
        )
    else:
        await message.answer(
            "Медиа больше не осталось. Перехожу к добавлению новых.",
            reply_markup=back_menu,
        )
        await state.set_state(EditService.adding_media)


@router.message(EditService.adding_media, F.content_type.in_(["photo", "video"]))
async def collect_new_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(message.bot, file_id, MEDIA_PATH, is_video)
    data = await state.get_data()
    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(EditService.adding_media, F.text.lower() == "готово")
async def save_service_changes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    services = load_json(JSON_PATH)

    for svc in services:
        if svc["title"] == data["title"]:
            if "desc" in data:
                svc["desc"] = data["desc"]
            if "media" in data:
                svc["media"] = data["media"]
            break

    save_json(JSON_PATH, services)
    await state.set_state(ManageService.choosing_action)
    await message.answer("✏️ Услуга обновлена")
