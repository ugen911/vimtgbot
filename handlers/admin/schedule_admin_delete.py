from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR
from handlers.admin.base_crud import load_json, save_json
from keyboards.main_menu import back_menu
from .schedule_admin_states import ManageSchedule

router = Router()

JSON_PATH = os.path.join(DATA_DIR, "расписание.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, "расписание")


@router.message(ManageSchedule.choosing_action, F.text == "🗑 Удалить расписание")
async def choose_block_to_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    group = data["group"]
    blocks = load_json(JSON_PATH).get(group, [])

    if not blocks:
        return await message.answer("📭 Блоков расписания нет.")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManageSchedule.choosing_block_to_delete)
    await message.answer(
        "Выберите блок для удаления или '🔙 Назад':", reply_markup=keyboard
    )


@router.message(ManageSchedule.choosing_block_to_delete)
async def process_block_deletion(message: types.Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    group = data["group"]

    if text.lower() in ["🔙 назад", "отмена"]:
        await state.set_state(ManageSchedule.choosing_action)
        return await message.answer(
            "↩️ Возврат в меню действий.", reply_markup=back_menu
        )

    if not text or ":" not in text or not text.split(":")[0].isdigit():
        return await message.answer("❌ Неверный формат. Выберите из списка.")

    index = int(text.split(":")[0]) - 1
    schedule = load_json(JSON_PATH)

    if not (0 <= index < len(schedule[group])):
        return await message.answer("❌ Блок не найден. Попробуйте снова.")

    # Удаление медиа
    for file in schedule[group][index].get("media", []):
        try:
            os.remove(os.path.join(MEDIA_PATH, group, file))
        except FileNotFoundError:
            pass

    del schedule[group][index]
    save_json(JSON_PATH, schedule)

    # Повторный выбор, если остались блоки
    updated_blocks = schedule.get(group, [])
    if updated_blocks:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
                for i, b in enumerate(updated_blocks)
            ]
            + [[types.KeyboardButton(text="🔙 Назад")]],
            resize_keyboard=True,
        )
        await message.answer(
            "🗑 Блок удалён. Выберите следующий для удаления или '🔙 Назад':",
            reply_markup=keyboard,
        )
        return

    await state.set_state(ManageSchedule.choosing_action)
    await message.answer("🗑 Все блоки удалены. Возврат в меню.", reply_markup=back_menu)
