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
        return await message.answer("Список пуст")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
            for i, b in enumerate(blocks)
        ]
        + [[types.KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
    )
    await state.set_state(ManageSchedule.choosing_block)
    await state.update_data(action="delete")
    await message.answer("Выберите блок для удаления:", reply_markup=keyboard)


@router.message(ManageSchedule.choosing_block, F.text.regexp(r"^\d+:"))
async def process_block_deletion(message: types.Message, state: FSMContext):
    index = int(message.text.split(":")[0]) - 1
    data = await state.get_data()
    group = data["group"]
    schedule = load_json(JSON_PATH)

    if 0 <= index < len(schedule[group]):
        for file in schedule[group][index].get("media", []):
            try:
                os.remove(os.path.join(MEDIA_PATH, group, file))
            except FileNotFoundError:
                pass
        del schedule[group][index]
        save_json(JSON_PATH, schedule)

        # Повторный выбор, если ещё есть блоки
        blocks = schedule.get(group, [])
        if blocks:
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text=f"{i+1}: {b['desc'][:30]}")]
                    for i, b in enumerate(blocks)
                ]
                + [[types.KeyboardButton(text="🔙 Назад")]],
                resize_keyboard=True,
            )
            return await message.answer(
                "🗑 Блок удалён. Выберите следующий или '🔙 Назад':",
                reply_markup=keyboard,
            )

    await state.set_state(ManageSchedule.choosing_action)
    await message.answer(
        "🗑 Блок удалён. Других блоков не осталось.", reply_markup=back_menu
    )
