from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json, save_media_file
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu, action_menu  # ✅ добавлено меню действий

router = Router()
router.message.filter(IsAdmin())

JSON_PATH = os.path.join(DATA_DIR, "расписание.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "расписание")


class EditSchedule(StatesGroup):
    choosing_group = State()
    entering_desc = State()
    entering_media = State()


class ManageSchedule(StatesGroup):
    choosing_group = State()
    choosing_action = State()
    choosing_block = State()
    editing_desc = State()
    editing_media = State()


@router.message(F.text == "/admin_schedule")
async def schedule_admin_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    group_keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="👶 Младшая группа"),
                types.KeyboardButton(text="🧒 Старшая группа"),
            ],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу:", reply_markup=group_keyboard)
    await state.set_state(ManageSchedule.choosing_group)


@router.message(
    ManageSchedule.choosing_group,
    F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"]),
)
async def schedule_group_selected(message: types.Message, state: FSMContext):
    group = "младшая" if "Младшая" in message.text else "старшая"
    await state.update_data(group=group)
    await state.set_state(ManageSchedule.choosing_action)
    await message.answer(
        f"Вы выбрали {message.text}. Что хотите сделать?", reply_markup=action_menu
    )


@router.message(ManageSchedule.choosing_action, F.text == "➕ Добавить")
async def start_adding_schedule(message: types.Message, state: FSMContext):
    await state.set_state(EditSchedule.entering_desc)
    await message.answer("Введите описание блока:", reply_markup=back_menu)


@router.message(EditSchedule.entering_desc)
async def input_schedule_desc(message: types.Message, state: FSMContext):
    await state.update_data(desc=message.text.strip())
    await state.set_state(EditSchedule.entering_media)
    await message.answer(
        "Отправьте медиа или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(EditSchedule.entering_media, F.content_type.in_(["photo", "video"]))
async def collect_schedule_media(message: types.Message, state: FSMContext):
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


@router.message(EditSchedule.entering_media, F.text.lower() == "готово")
async def finish_add_schedule(message: types.Message, state: FSMContext):
    data = await state.get_data()
    schedule = load_json(JSON_PATH)
    group = data["group"]
    schedule.setdefault(group, []).append(
        {"desc": data["desc"], "media": data.get("media", [])}
    )
    save_json(JSON_PATH, schedule)
    await state.clear()
    await message.answer("✅ Блок добавлен", reply_markup=action_menu)


@router.message(ManageSchedule.choosing_action, F.text.in_(["✏️ Изменить", "🗑 Удалить"]))
async def choose_block_to_edit_or_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    action = message.text
    blocks = load_json(JSON_PATH).get(group, [])

    if not blocks:
        return await message.answer("Список пуст", reply_markup=action_menu)

    await state.update_data(action=action)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManageSchedule.choosing_block)
    await message.answer("Выберите блок:", reply_markup=keyboard)


@router.message(ManageSchedule.choosing_block, F.text.regexp(r"^\d+:"))
async def process_block_selection(message: types.Message, state: FSMContext):
    index = int(message.text.split(":")[0]) - 1
    data = await state.get_data()
    group = data["group"]
    schedule = load_json(JSON_PATH)

    if data["action"] == "🗑 Удалить":
        if 0 <= index < len(schedule[group]):
            del schedule[group][index]
            save_json(JSON_PATH, schedule)
            await state.clear()
            return await message.answer("🗑 Блок удалён", reply_markup=action_menu)

    await state.update_data(block_idx=index)
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
    schedule[group][idx] = {"desc": data["desc"], "media": data.get("media", [])}
    save_json(JSON_PATH, schedule)
    await state.clear()
    await message.answer("✏️ Блок обновлён", reply_markup=action_menu)
