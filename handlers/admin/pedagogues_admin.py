from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import ADMINS
from keyboards.main_menu import back_menu
from filters.is_admin import IsAdmin
from .pedagogues_admin_states import ManagePedagogue, EditPedagogue

# Подроутеры
from .pedagogues_admin_add import router as add_router
from .pedagogues_admin_edit import router as edit_router
from .pedagogues_admin_delete import router as delete_router

router = Router()
router.message.filter(IsAdmin())

# Подключаем все подмодули
router.include_router(add_router)
router.include_router(edit_router)
router.include_router(delete_router)


@router.message(F.text == "/admin_pedagogues")
async def admin_pedagogues_menu(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ Доступ запрещен")

    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👩‍🏫 Воспитатели")],
            [types.KeyboardButton(text="🎨 Преподаватели")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("👥 Выберите категорию педагогов:", reply_markup=keyboard)
    await state.set_state(ManagePedagogue.choosing_role)


@router.message(
    ManagePedagogue.choosing_role, F.text.in_(["👩‍🏫 Воспитатели", "🎨 Преподаватели"])
)
async def handle_role_selection(message: types.Message, state: FSMContext):
    role = "воспитатели" if "Воспитатели" in message.text else "преподаватели"
    await state.update_data(role=role)
    await state.set_state(ManagePedagogue.choosing_action)

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Добавить педагога")],
            [types.KeyboardButton(text="✏️ Изменить педагога")],
            [types.KeyboardButton(text="🗑 Удалить педагога")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"Вы выбрали: {message.text}. Что хотите сделать?", reply_markup=keyboard
    )


@router.message(ManagePedagogue.choosing_action, F.text == "➕ Добавить педагога")
async def start_add_pedagogue(message: types.Message, state: FSMContext):
    await state.set_state(EditPedagogue.waiting_for_name)
    await message.answer(
        "Введите имя педагога или напишите 'Пропустить':", reply_markup=back_menu
    )
