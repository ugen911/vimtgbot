from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .pedagogues_admin_states import ManagePedagogue

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "pedagogues.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "педагоги")


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

    # Удаление медиа
    for file in items[index].get("media", []):
        try:
            os.remove(os.path.join(MEDIA_PATH, role, file))
        except FileNotFoundError:
            pass

    del all_data[role][index]
    save_json(JSON_PATH, all_data)

    # Повторный выбор, если остались
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
