# online_tour_admin_delete.py
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .online_tour_admin_states import DeleteTour, ManageTour

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(ManageTour.choosing_action, F.text == "🗑 Удалить экскурсию")
async def start_delete_tour(message: types.Message, state: FSMContext):
    blocks = load_json(JSON_PATH)
    if not blocks:
        return await message.answer("Список пуст")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(DeleteTour.waiting_for_selection)
    await message.answer("Выберите экскурсию для удаления:", reply_markup=keyboard)


@router.message(DeleteTour.waiting_for_selection, F.text.regexp(r"^\d+:"))
async def delete_selected_tour(message: types.Message, state: FSMContext):
    blocks = load_json(JSON_PATH)
    idx = int(message.text.split(":")[0]) - 1

    if not (0 <= idx < len(blocks)):
        return await message.answer("❌ Неверный выбор.")

    for file in blocks[idx].get("media", []):
        try:
            os.remove(os.path.join(MEDIA_PATH, file))
        except FileNotFoundError:
            pass

    del blocks[idx]
    save_json(JSON_PATH, blocks)

    if not blocks:
        await state.set_state(ManageTour.choosing_action)
        return await message.answer(
            "🗑 Экскурсия удалена. Список пуст.", reply_markup=back_menu
        )

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await message.answer(
        "🗑 Экскурсия удалена. Выберите следующую или '🔙 Назад':", reply_markup=keyboard
    )


@router.message(DeleteTour.waiting_for_selection, F.text == "🔙 Назад")
async def cancel_delete_tour(message: types.Message, state: FSMContext):
    await state.set_state(ManageTour.choosing_action)
    await message.answer("↩️ Возврат в меню.", reply_markup=back_menu)
