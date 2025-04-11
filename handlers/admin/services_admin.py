from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu  # ✅ Добавили общий "Назад"

router = Router()
router.message.filter(IsAdmin())

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


class AddService(StatesGroup):
    waiting_for_title = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class DeleteService(StatesGroup):
    waiting_for_selection = State()


class EditService(StatesGroup):
    waiting_for_service_choice = State()
    waiting_for_new_desc = State()
    waiting_for_new_media = State()


@router.message(F.text == "/admin_services")
async def admin_services_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await message.answer(
        "🔧 Управление услугами:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="➕ Добавить услугу")],
                [types.KeyboardButton(text="🗑 Удалить услугу")],
                [types.KeyboardButton(text="✏️ Изменить услугу")],
                [types.KeyboardButton(text="🔙 Назад")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(F.text == "➕ Добавить услугу")
async def start_add_service(message: types.Message, state: FSMContext):
    await state.set_state(AddService.waiting_for_title)
    await message.answer("Введите заголовок новой услуги:", reply_markup=back_menu)


@router.message(AddService.waiting_for_title)
async def process_service_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(AddService.waiting_for_desc)
    await message.answer("Введите описание услуги:", reply_markup=back_menu)


@router.message(AddService.waiting_for_desc)
async def process_service_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(AddService.waiting_for_media)
    await message.answer(
        "Отправьте медиафайлы (фото/видео). Когда закончите — напишите 'Готово'",
        reply_markup=back_menu,
    )


@router.message(AddService.waiting_for_media, F.text.lower() == "готово")
async def finish_add_service(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    desc = data["desc"]
    media = data.get("media", [])

    services = load_json(JSON_PATH)
    services.append({"title": title, "desc": desc, "media": media})
    save_json(JSON_PATH, services)

    await state.clear()
    await message.answer("✅ Услуга добавлена", reply_markup=back_menu)


@router.message(AddService.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_service_media(message: types.Message, state: FSMContext):
    media_list = []
    if message.photo:
        file_id = message.photo[-1].file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=False
        )
        media_list.append(filename)
    elif message.video:
        file_id = message.video.file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=True
        )
        media_list.append(filename)

    state_data = await state.get_data()
    all_media = state_data.get("media", []) + media_list
    await state.update_data(media=all_media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")


@router.message(F.text == "🗑 Удалить услугу")
async def start_delete_service(message: types.Message, state: FSMContext):
    services = load_json(JSON_PATH)
    if not services:
        return await message.answer("Список услуг пуст.", reply_markup=back_menu)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=svc["title"])] for svc in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteService.waiting_for_selection)
    await message.answer("Выберите услугу для удаления:", reply_markup=keyboard)


@router.message(DeleteService.waiting_for_selection)
async def process_delete_selection(message: types.Message, state: FSMContext):
    title_to_delete = message.text.strip()
    services = load_json(JSON_PATH)

    new_services = [svc for svc in services if svc["title"] != title_to_delete]
    if len(new_services) == len(services):
        return await message.answer("❌ Услуга не найдена.", reply_markup=back_menu)

    save_json(JSON_PATH, new_services)
    await state.clear()
    await message.answer("🗑 Услуга удалена.", reply_markup=back_menu)


@router.message(F.text == "✏️ Изменить услугу")
async def start_edit_service(message: types.Message, state: FSMContext):
    services = load_json(JSON_PATH)
    if not services:
        return await message.answer("Список услуг пуст.", reply_markup=back_menu)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=svc["title"])] for svc in services]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(EditService.waiting_for_service_choice)
    await message.answer("Выберите услугу для редактирования:", reply_markup=keyboard)


@router.message(EditService.waiting_for_service_choice)
async def ask_new_description(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await state.set_state(EditService.waiting_for_new_desc)
    await message.answer("Введите новое описание:", reply_markup=back_menu)


@router.message(EditService.waiting_for_new_desc)
async def ask_new_media(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(EditService.waiting_for_new_media)
    await message.answer(
        "Отправьте новые медиафайлы или напишите 'Готово':", reply_markup=back_menu
    )


@router.message(EditService.waiting_for_new_media, F.text.lower() == "готово")
async def save_edited_service(message: types.Message, state: FSMContext):
    data = await state.get_data()
    services = load_json(JSON_PATH)

    for svc in services:
        if svc["title"] == data["title"]:
            svc["desc"] = data["desc"]
            svc["media"] = data.get("media", [])
            break

    save_json(JSON_PATH, services)
    await state.clear()
    await message.answer("✏️ Услуга обновлена.", reply_markup=back_menu)


@router.message(
    EditService.waiting_for_new_media, F.content_type.in_(["photo", "video"])
)
async def collect_new_media(message: types.Message, state: FSMContext):
    media_list = []
    if message.photo:
        file_id = message.photo[-1].file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=False
        )
        media_list.append(filename)
    elif message.video:
        file_id = message.video.file_id
        filename = await save_media_file(
            message.bot, file_id, MEDIA_PATH, is_video=True
        )
        media_list.append(filename)

    state_data = await state.get_data()
    all_media = state_data.get("media", []) + media_list
    await state.update_data(media=all_media)
    await message.answer("📎 Медиа добавлено. Отправьте ещё или напишите 'Готово'")
