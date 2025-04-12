from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json, save_media_file
from keyboards.main_menu import back_menu
from .pedagogues_admin_states import EditPedagogue

router = Router()

MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")
JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")


@router.message(EditPedagogue.waiting_for_name)
async def add_pedagogue_name(message: types.Message, state: FSMContext):
    if message.text.strip().lower() != "пропустить":
        await state.update_data(name=message.text.strip())
    else:
        await state.update_data(name="Без имени")
    await state.set_state(EditPedagogue.waiting_for_role)
    await message.answer(
        "Введите должность (роль) педагога или напишите 'Пропустить':",
        reply_markup=back_menu,
    )


@router.message(EditPedagogue.waiting_for_role)
async def add_pedagogue_role(message: types.Message, state: FSMContext):
    role_text = message.text.strip().lower()
    if role_text != "пропустить":
        await state.update_data(role_title=message.text.strip())
    else:
        await state.update_data(role_title="Педагог")
    await state.set_state(EditPedagogue.waiting_for_description)
    await message.answer(
        "Введите описание педагога или напишите 'Пропустить':", reply_markup=back_menu
    )


@router.message(EditPedagogue.waiting_for_description)
async def add_pedagogue_description(message: types.Message, state: FSMContext):
    if (message.text or "").strip().lower() != "пропустить":
        await state.update_data(description=message.text.strip())
    else:
        await state.update_data(description="")
    await state.update_data(media=[])
    await state.set_state(EditPedagogue.waiting_for_media)
    await message.answer(
        "Отправьте медиа (фото/видео), или напишите 'Готово'", reply_markup=back_menu
    )


@router.message(EditPedagogue.waiting_for_media, F.content_type.in_(["photo", "video"]))
async def collect_pedagogue_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    is_video = bool(message.video)
    data = await state.get_data()

    # Папка по роли педагога
    folder = data.get(
        "role", "воспитатели"
    )  # ← ожидаем "воспитатели" или "преподаватели"
    media_path = os.path.join(MEDIA_PATH, folder)
    os.makedirs(media_path, exist_ok=True)

    filename = await save_media_file(message.bot, file_id, media_path, is_video)

    media = data.get("media", [])
    media.append(filename)
    await state.update_data(media=media)
    await message.answer("📎 Медиа добавлено. Ещё или напишите 'Готово'")


@router.message(EditPedagogue.waiting_for_media, F.text.lower() == "готово")
async def finish_add_pedagogue(message: types.Message, state: FSMContext):
    data = await state.get_data()
    folder = data.get("role", "воспитатели")  # ← ключ для JSON и папки
    all_data = load_json(JSON_PATH)

    new_pedagogue = {
        "name": data.get("name", "Без имени"),
        "role": data.get("role_title", "Педагог"),
        "description": data.get("description", ""),
        "media": data.get("media", []),
    }

    all_data.setdefault(folder, []).append(new_pedagogue)
    save_json(JSON_PATH, all_data)

    await state.clear()
    await message.answer(
        "✅ Педагог добавлен",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="🔙 Назад")]],
            resize_keyboard=True,
        ),
    )
