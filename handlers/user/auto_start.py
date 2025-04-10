from aiogram import Router, types
from aiogram.filters.command import Command
from keyboards.main_menu import main_menu
from handlers.user.state import user_states

router = Router()


@router.message(~Command("admin"))
async def ensure_start(message: types.Message):
    user_id = message.from_user.id

    if not user_states.get(user_id):
        user_states[user_id] = True
        await message.answer(
            '🏡 <b>Добро пожаловать в детский сад "Виммельбух"! 👶</b>\n\n'
            "Выберите интересующий раздел из меню ниже:",
            reply_markup=main_menu,
        )
    elif message.reply_markup is None:
        await message.answer("🔄 Возвращаемся в главное меню:", reply_markup=main_menu)
