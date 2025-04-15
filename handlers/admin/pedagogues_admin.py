from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from filters.is_admin import IsAdmin
from .pedagogues_admin_states import ManagePedagogue, EditPedagogue

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_ROOT = os.path.join(MEDIA_DIR, "педагоги")

# Подключаем подроутеры для добавления, редактирования и удаления педагогов
from .pedagogues_admin_add import router as add_router
from .pedagogues_admin_edit import router as edit_router
from .pedagogues_admin_delete import router as delete_router

router = Router()
router.message.filter(IsAdmin())
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)


# Новый обработчик для входа в админку педагогов
@router.message(IsAdmin(), F.text == "/admin_pedagogues")
async def admin_pedagogues_menu(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👩‍🏫 Воспитатели")],
            [types.KeyboardButton(text="🎓 Преподаватели")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите категорию педагогов:", reply_markup=keyboard)
    await state.set_state(ManagePedagogue.choosing_role)


# Обработчик выбора категории педагогов
@router.message(
    ManagePedagogue.choosing_role, F.text.in_(["👩‍🏫 Воспитатели", "🎓 Преподаватели"])
)
async def set_pedagogue_role(message: types.Message, state: FSMContext):
    role = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    await state.update_data(role=role)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить педагога")],
            [types.KeyboardButton(text="✏️ Изменить педагога")],
            [types.KeyboardButton(text="🗑 Удалить педагога")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(ManagePedagogue.choosing_action)


# Новый обработчик для кнопки "➕ Добавить педагога"
@router.message(ManagePedagogue.choosing_action, F.text == "➕ Добавить педагога")
async def admin_add_pedagogue(message: types.Message, state: FSMContext):
    # Переход в состояние добавления педагога. Значение "role" (категория) уже сохранено.
    await state.set_state(EditPedagogue.waiting_for_name)
    await message.answer(
        "Введите имя педагога или напишите 'Пропустить':", reply_markup=back_menu
    )


def delete_media_files(filenames: list[str], role: str):
    media_path = os.path.join(MEDIA_ROOT, role)
    deleted = 0
    for file in filenames:
        path = os.path.join(media_path, file)
        if os.path.exists(path):
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении {path}: {e}")
        else:
            print(f"[WARNING] Файл не найден: {path}")
    print(f"[INFO] Удалено файлов: {deleted} (роль: {role})")


@router.message(ManagePedagogue.choosing_action, F.text == "🗑 Удалить педагога")
async def choose_pedagogue_for_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    role = data.get("role")
    all_data = load_json(JSON_PATH)
    items = all_data.get(role, [])

    if not items:
        return await message.answer("📭 Список педагогов пуст.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["name"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManagePedagogue.deleting_name)
    await message.answer(
        "Выберите педагога для удаления или '🔙 Назад':", reply_markup=keyboard
    )


@router.message(ManagePedagogue.deleting_name)
async def delete_pedagogue(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if name.lower() in ["🔙 назад", "отмена"]:
        await state.set_state(ManagePedagogue.choosing_action)
        return await message.answer("↩️ Возврат в меню.", reply_markup=back_menu)

    data = await state.get_data()
    role = data.get("role")
    all_data = load_json(JSON_PATH)
    items = all_data.get(role, [])

    index = next((i for i, p in enumerate(items) if p["name"] == name), -1)

    if index == -1:
        return await message.answer("❌ Педагог не найден. Выберите из списка.")

    delete_media_files(items[index].get("media", []), role)
    del all_data[role][index]
    save_json(JSON_PATH, all_data)

    remaining = all_data.get(role, [])
    if not remaining:
        await state.set_state(ManagePedagogue.choosing_action)
        return await message.answer(
            "🗑 Педагог удалён. Список пуст.", reply_markup=back_menu
        )

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["name"])] for item in remaining]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer(
        "🗑 Педагог удалён. Выберите следующего или '🔙 Назад':", reply_markup=keyboard
    )
