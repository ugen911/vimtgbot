from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .eat_admin_states import DeleteMenu, ManageMenu

router = Router()

SECTION_TITLE = "🍽 Меню"
SECTION_KEY = "menu"
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageMenu.choosing_action, F.text == "🗑 Удалить меню")
async def start_delete_menu(message: types.Message, state: FSMContext):
    data = load_json(JSON_PATH)

    # 🛡️ Защита
    if isinstance(data, list):
        data = {"menu_items": data}
    elif not isinstance(data, dict):
        data = {"menu_items": []}

    items = data.get("menu_items", [])
    if not items:
        return await message.answer("Меню пока пусто.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=item["description"])] for item in items]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteMenu.waiting_for_selection)
    await message.answer("Выберите блок меню для удаления:", reply_markup=keyboard)


@router.message(DeleteMenu.waiting_for_selection)
async def delete_menu_block(message: types.Message, state: FSMContext):
    desc = message.text.strip()
    if desc == "🔙 Назад" or desc.lower() == "отмена":
        await state.set_state(ManageMenu.choosing_action)
        return await message.answer("↩️ Возврат в меню.", reply_markup=back_menu)

    data = load_json(JSON_PATH)

    # 🛡️ Защита
    if isinstance(data, list):
        data = {"menu_items": data}
    elif not isinstance(data, dict):
        data = {"menu_items": []}

    blocks = data.get("menu_items", [])
    new_blocks = []
    found = False

    for block in blocks:
        if block["description"] == desc:
            for file in block.get("media", []):
                try:
                    os.remove(os.path.join(MEDIA_PATH, file))
                except FileNotFoundError:
                    pass
            found = True
        else:
            new_blocks.append(block)

    if not found:
        return await message.answer("❌ Блок меню не найден. Попробуйте ещё раз.")

    data["menu_items"] = new_blocks
    save_json(JSON_PATH, data)

    if not new_blocks:
        await state.set_state(ManageMenu.choosing_action)
        return await message.answer(
            "🗑 Блок удалён. Меню теперь пустое.", reply_markup=back_menu
        )

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=item["description"])] for item in new_blocks
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer(
        "🗑 Блок удалён. Выберите следующий или '🔙 Назад':", reply_markup=keyboard
    )
