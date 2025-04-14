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


def delete_media_files(filenames: list[str]):
    deleted = 0
    for file in filenames:
        path = os.path.join(MEDIA_PATH, file)
        if os.path.exists(path):
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(f"[ERROR] Ошибка при удалении {path}: {e}")
        else:
            print(f"[WARNING] Файл не найден: {path}")
    print(f"[INFO] Удалено файлов: {deleted}")


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

    delete_media_files(blocks[idx].get("media", []))
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
