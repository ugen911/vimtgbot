from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import (
    back_menu,
    action_menu,
)  # ✅ добавим универсальное меню действий

router = Router()
router.message.filter(IsAdmin())

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


class EditPedagogue(StatesGroup):
    waiting_for_role = State()
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_media = State()


class ManagePedagogue(StatesGroup):
    choosing_role = State()
    choosing_action = State()
    choosing_name = State()
    editing_description = State()
    editing_media = State()


@router.message(F.text == "/admin_pedagogues")
async def admin_pedagogues_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👩‍🏫 Воспитатели"),
                types.KeyboardButton(text="🎓 Преподаватели"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)
    await state.set_state(ManagePedagogue.choosing_role)


@router.message(
    ManagePedagogue.choosing_role, F.text.in_(["👩‍🏫 Воспитатели", "🎓 Преподаватели"])
)
async def ask_action_for_role(message: types.Message, state: FSMContext):
    role = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    await state.update_data(role=role)
    await state.set_state(ManagePedagogue.choosing_action)
    await message.answer(
        f"Вы выбрали {message.text}. Что хотите сделать?", reply_markup=action_menu
    )


@router.message(ManagePedagogue.choosing_action, F.text == "➕ Добавить")
async def start_add_pedagogue(message: types.Message, state: FSMContext):
    await state.set_state(EditPedagogue.waiting_for_name)
    await message.answer("Введите имя педагога:", reply_markup=back_menu)


@router.message(EditPedagogue.waiting_for_name)
async def get_pedagogue_description(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(EditPedagogue.waiting_for_description)
    await message.answer("Введите описание педагога:", reply_markup=back_menu)


@router.message(EditPedagogue.waiting_for_description)
async def get_pedagogue_media(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(EditPedagogue.waiting_for_media)
    await message.answer(
        "Отправьте медиа (фото/видео), или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(EditPedagogue.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_new_pedagogue_media(message: types.Message, state: FSMContext):
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
async def finish_add_pedagogue(message: types.Message, state: FSMContext):
    data = await state.get_data()
    all_data = load_json(JSON_PATH)
    all_data.setdefault(data["role"], []).append(
        {
            "name": data["name"],
            "role": "Воспитатель" if data["role"] == "воспитатели" else "Преподаватель",
            "description": data["description"],
            "media": data.get("media", []),
        }
    )
    save_json(JSON_PATH, all_data)
    await state.clear()
    await message.answer("✅ Педагог добавлен", reply_markup=action_menu)


@router.message(
    ManagePedagogue.choosing_action, F.text.in_(["✏️ Изменить", "🗑 Удалить"])
)
async def choose_pedagogue_for_edit_or_delete(
    message: types.Message, state: FSMContext
):
    action = message.text
    data = await state.get_data()
    role = data["role"]
    data["action"] = action
    await state.update_data(action=action)

    all_data = load_json(JSON_PATH)
    names = [p["name"] for p in all_data.get(role, [])]

    if not names:
        return await message.answer("Список пуст.", reply_markup=action_menu)

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
        return await message.answer("❌ Не найдено", reply_markup=action_menu)

    await state.update_data(name=name, index=index)

    if data["action"] == "🗑 Удалить":
        del all_data[role][index]
        save_json(JSON_PATH, all_data)
        await state.clear()
        return await message.answer("🗑 Удалено", reply_markup=action_menu)

    await state.set_state(ManagePedagogue.editing_description)
    await message.answer("Введите новое описание:", reply_markup=back_menu)


@router.message(ManagePedagogue.editing_description)
async def edit_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(ManagePedagogue.editing_media)
    await message.answer("Отправьте новые медиа или 'Готово'", reply_markup=back_menu)


@router.message(ManagePedagogue.editing_media, F.content_type.in_(["photo", "video"]))
async def collect_edited_media(message: types.Message, state: FSMContext):
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
    all_data[data["role"]][data["index"]]["description"] = data["description"]
    all_data[data["role"]][data["index"]]["media"] = data.get("media", [])
    save_json(JSON_PATH, all_data)
    await state.clear()
    await message.answer("✏️ Обновлено", reply_markup=action_menu)
