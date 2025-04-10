from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


class EditPedagogue(StatesGroup):
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_media = State()


class ManagePedagogue(StatesGroup):
    choosing_role = State()
    choosing_name = State()
    editing_description = State()
    editing_media = State()


@router.message(F.text == "/admin_pedagogues")
async def admin_pedagogues_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👩‍🏫 Воспитатели"),
                types.KeyboardButton(text="🎓 Преподаватели"),
            ],
            [
                types.KeyboardButton(text="✏️ Редактировать"),
                types.KeyboardButton(text="🗑 Удалить"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await message.bot.get_fsm_context(message.chat.id).set_state(
        EditPedagogue.waiting_for_role
    )


@router.message(
    EditPedagogue.waiting_for_role, F.text.in_(["👩‍🏫 Воспитатели", "🎓 Преподаватели"])
)
async def get_pedagogue_name(message: types.Message, state: FSMContext):
    role_key = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    await state.update_data(role=role_key)
    await state.set_state(EditPedagogue.waiting_for_name)
    await message.answer("Введите имя педагога:")


@router.message(EditPedagogue.waiting_for_name)
async def get_pedagogue_description(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(EditPedagogue.waiting_for_description)
    await message.answer("Введите описание педагога:")


@router.message(EditPedagogue.waiting_for_description)
async def get_pedagogue_media(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(EditPedagogue.waiting_for_media)
    await message.answer(
        "Отправьте медиафайлы (фото/видео), когда закончите — напишите 'Готово'"
    )


@router.message(EditPedagogue.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_pedagogue_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]
    media_path = os.path.join(MEDIA_PATH, role)

    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    filename = await save_media_file(
        message.bot, file_id, media_path, is_video=is_video
    )

    media_list = data.get("media", [])
    media_list.append(filename)
    await state.update_data(media=media_list)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(EditPedagogue.waiting_for_media, F.text.lower() == "готово")
async def save_pedagogue(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]
    name = data["name"]
    description = data["description"]
    media = data.get("media", [])

    all_data = load_json(JSON_PATH)
    all_data.setdefault(role, []).append(
        {
            "name": name,
            "role": "Воспитатель" if role == "воспитатели" else "Преподаватель",
            "description": description,
            "media": media,
        }
    )
    save_json(JSON_PATH, all_data)

    await state.clear()
    await message.answer("✅ Педагог добавлен")


@router.message(F.text == "🗑 Удалить")
async def delete_pedagogue_start(message: types.Message, state: FSMContext):
    await state.set_state(ManagePedagogue.choosing_role)
    await message.answer(
        "Выберите категорию:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="👩‍🏫 Воспитатели"),
                    types.KeyboardButton(text="🎓 Преподаватели"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@router.message(F.text == "✏️ Редактировать")
async def edit_pedagogue_start(message: types.Message, state: FSMContext):
    await state.set_state(ManagePedagogue.choosing_role)
    await message.answer(
        "Выберите категорию:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [
                    types.KeyboardButton(text="👩‍🏫 Воспитатели"),
                    types.KeyboardButton(text="🎓 Преподаватели"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@router.message(
    ManagePedagogue.choosing_role, F.text.in_(["👩‍🏫 Воспитатели", "🎓 Преподаватели"])
)
async def list_pedagogues_by_role(message: types.Message, state: FSMContext):
    role_key = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    data = load_json(JSON_PATH)
    names = [p["name"] for p in data.get(role_key, [])]

    if not names:
        return await message.answer("Список пуст")

    await state.update_data(role=role_key)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=name)] for name in names],
        resize_keyboard=True,
    )
    await state.set_state(ManagePedagogue.choosing_name)
    await message.answer("Выберите имя:", reply_markup=keyboard)


@router.message(ManagePedagogue.choosing_name)
async def confirm_edit_or_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data["role"]
    name = message.text.strip()
    all_data = load_json(JSON_PATH)
    index = next((i for i, p in enumerate(all_data[role]) if p["name"] == name), -1)

    if index == -1:
        return await message.answer("❌ Не найдено")

    await state.update_data(name=name, index=index)
    if state.state == ManagePedagogue.choosing_name:
        await state.set_state(ManagePedagogue.editing_description)
        await message.answer("Введите новое описание:")


@router.message(ManagePedagogue.editing_description)
async def edit_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(ManagePedagogue.editing_media)
    await message.answer("Отправьте новые медиа или 'Готово'")


@router.message(ManagePedagogue.editing_media, F.content_type.in_(["photo", "video"]))
async def collect_edit_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    data = await state.get_data()
    media_path = os.path.join(MEDIA_PATH, data["role"])
    filename = await save_media_file(
        message.bot, file_id, media_path, is_video=is_video
    )

    media_list = data.get("media", [])
    media_list.append(filename)
    await state.update_data(media=media_list)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(ManagePedagogue.editing_media, F.text.lower() == "готово")
async def finish_editing(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_data = load_json(JSON_PATH)

    role = data["role"]
    idx = data["index"]
    all_data[role][idx]["description"] = data["description"]
    all_data[role]["media"] = data.get("media", [])

    save_json(JSON_PATH, all_data)
    await message.answer("✏️ Обновлено")
    await state.clear()


@router.message(ManagePedagogue.editing_description, F.text.lower() == "удалить")
async def finish_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_data = load_json(JSON_PATH)
    role = data["role"]
    idx = data["index"]
    del all_data[role][idx]
    save_json(JSON_PATH, all_data)
    await message.answer("🗑 Удалено")
    await state.clear()
