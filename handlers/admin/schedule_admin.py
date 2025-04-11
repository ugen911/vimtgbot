from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu  # ✅ Единое меню "Назад"

router = Router()
router.message.filter(IsAdmin())

JSON_PATH = os.path.join(DATA_DIR, "расписание.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "расписание")


class EditSchedule(StatesGroup):
    waiting_for_group = State()
    waiting_for_day = State()
    waiting_for_desc = State()
    waiting_for_media = State()


class ManageSchedule(StatesGroup):
    waiting_for_group_choice = State()
    waiting_for_block_selection = State()
    waiting_for_new_desc = State()
    waiting_for_new_media = State()


@router.message(F.text == "/admin_schedule")
async def schedule_admin_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить расписание")],
            [
                types.KeyboardButton(text="✏️ Редактировать"),
                types.KeyboardButton(text="🗑 Удалить"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("📅 Меню управления расписанием:", reply_markup=keyboard)


@router.message(F.text == "➕ Добавить расписание")
async def add_schedule_select_group(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👶 Младшая группа"),
                types.KeyboardButton(text="🧒 Старшая группа"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу:", reply_markup=keyboard)
    await state.set_state(EditSchedule.waiting_for_group)


@router.message(
    EditSchedule.waiting_for_group,
    F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"]),
)
async def choose_day_for_group(message: types.Message, state: FSMContext):
    group_key = "младшая" if "Младшая" in message.text else "старшая"
    await state.update_data(group=group_key)
    await state.set_state(EditSchedule.waiting_for_day)
    await message.answer("Введите день недели или тему блока:", reply_markup=back_menu)


@router.message(EditSchedule.waiting_for_day)
async def enter_schedule_description(message: types.Message, state: FSMContext):
    await state.update_data(day=message.text.strip())
    await state.set_state(EditSchedule.waiting_for_desc)
    await message.answer("Введите описание:", reply_markup=back_menu)


@router.message(EditSchedule.waiting_for_desc)
async def enter_schedule_media(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(EditSchedule.waiting_for_media)
    await message.answer(
        "Отправьте медиафайлы или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(EditSchedule.waiting_for_media, F.text.lower() == "готово")
async def finish_schedule_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    desc = data["desc"]
    media = data.get("media", [])

    schedule_data = load_json(JSON_PATH)
    schedule_data[group].append({"desc": desc, "media": media})
    save_json(JSON_PATH, schedule_data)

    await state.clear()
    await message.answer("✅ Расписание добавлено", reply_markup=back_menu)


@router.message(EditSchedule.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_schedule_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    data = await state.get_data()
    group_path = os.path.join(MEDIA_PATH, data["group"])
    filename = await save_media_file(
        message.bot, file_id, group_path, is_video=is_video
    )

    media_list = data.get("media", [])
    media_list.append(filename)
    await state.update_data(media=media_list)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(F.text == "🗑 Удалить")
async def start_delete_schedule(message: types.Message, state: FSMContext):
    await state.set_state(ManageSchedule.waiting_for_group_choice)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👶 Младшая группа"),
                types.KeyboardButton(text="🧒 Старшая группа"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу для удаления блока:", reply_markup=keyboard)


@router.message(
    ManageSchedule.waiting_for_group_choice,
    F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"]),
)
async def delete_block_select(message: types.Message, state: FSMContext):
    group = "младшая" if "Младшая" in message.text else "старшая"
    await state.update_data(group=group)
    data = load_json(JSON_PATH)
    blocks = data.get(group, [])

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManageSchedule.waiting_for_block_selection)
    await message.answer("Выберите блок для удаления:", reply_markup=keyboard)


@router.message(ManageSchedule.waiting_for_block_selection)
async def confirm_delete_block(message: types.Message, state: FSMContext):
    block_idx = int(message.text.split(":")[0]) - 1
    data = await state.get_data()
    group = data["group"]

    schedule_data = load_json(JSON_PATH)
    if 0 <= block_idx < len(schedule_data[group]):
        del schedule_data[group][block_idx]
        save_json(JSON_PATH, schedule_data)
        await state.clear()
        await message.answer("🗑 Блок удалён", reply_markup=back_menu)
    else:
        await message.answer("❌ Неверный номер блока", reply_markup=back_menu)


@router.message(F.text == "✏️ Редактировать")
async def start_edit_schedule(message: types.Message, state: FSMContext):
    await state.set_state(ManageSchedule.waiting_for_group_choice)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👶 Младшая группа"),
                types.KeyboardButton(text="🧒 Старшая группа"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "Выберите группу для редактирования блока:", reply_markup=keyboard
    )


@router.message(ManageSchedule.waiting_for_block_selection, F.text.regexp(r"^\d+:"))
async def prepare_edit_block(message: types.Message, state: FSMContext):
    block_idx = int(message.text.split(":")[0]) - 1
    await state.update_data(block_idx=block_idx)
    await state.set_state(ManageSchedule.waiting_for_new_desc)
    await message.answer("Введите новое описание:", reply_markup=back_menu)


@router.message(ManageSchedule.waiting_for_new_desc)
async def ask_new_block_media(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(ManageSchedule.waiting_for_new_media)
    await message.answer(
        "Отправьте новые медиа или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(
    ManageSchedule.waiting_for_new_media, F.content_type.in_(["photo", "video"])
)
async def collect_new_block_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    data = await state.get_data()
    group_path = os.path.join(MEDIA_PATH, data["group"])
    filename = await save_media_file(
        message.bot, file_id, group_path, is_video=is_video
    )

    media_list = data.get("media", [])
    media_list.append(filename)
    await state.update_data(media=media_list)
    await message.answer("📎 Медиа добавлено. Ещё или 'Готово'")


@router.message(ManageSchedule.waiting_for_new_media, F.text.lower() == "готово")
async def save_edited_block(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    idx = data["block_idx"]
    desc = data["desc"]
    media = data.get("media", [])

    schedule_data = load_json(JSON_PATH)
    if 0 <= idx < len(schedule_data[group]):
        schedule_data[group][idx] = {"desc": desc, "media": media}
        save_json(JSON_PATH, schedule_data)
        await message.answer("✏️ Блок обновлён", reply_markup=back_menu)
    await state.clear()
