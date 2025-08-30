from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import os
from config import DATA_DIR, MEDIA_DIR, ADMINS
from filters.is_admin import IsAdmin
from keyboards.main_menu import back_menu
from .schedule_admin_states import ManageSchedule

# Импорт вспомогательных модулей
from .schedule_admin_add import router as add_router
from .schedule_admin_edit import router as edit_router
from .schedule_admin_delete import router as delete_router  # ← новый импорт

router = Router()
router.message.filter(IsAdmin())

# Подключаем вспомогательные роутеры
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)  # ← подключение delete-модуля


@router.message(F.text == "/admin_schedule")
async def schedule_admin_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👶 Младшая группа")],
            [types.KeyboardButton(text="🧑 Средняя группа")],
            [types.KeyboardButton(text="🧒 Старшая группа")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу:", reply_markup=keyboard)
    await state.set_state(ManageSchedule.choosing_group)


@router.message(
    ManageSchedule.choosing_group,
    F.text.in_(["👶 Младшая группа", "🧑 Средняя группа", "🧒 Старшая группа"]),
)
async def schedule_group_selected(message: types.Message, state: FSMContext):
    if "Младшая" in message.text:
        group = "младшая"
    elif "Средняя" in message.text:
        group = "средняя"  
    else:
        group = "старшая"

    await state.update_data(group=group)
    await state.set_state(ManageSchedule.choosing_action)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить расписание")],
            [types.KeyboardButton(text="✏️ Изменить расписание")],
            [types.KeyboardButton(text="🗑 Удалить расписание")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"Вы выбрали {message.text}. Что хотите сделать?", reply_markup=keyboard
    )
