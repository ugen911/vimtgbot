from aiogram.filters import CommandStart
from aiogram import Router, types

from keyboards.main_menu import main_menu  # если меню у тебя отдельно

router = Router()


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(
        '🏡 <b>Добро пожаловать в детский сад "Виммельбух"! 👶</b>\n\n'
        "Выберите интересующий раздел из меню ниже:",
        reply_markup=main_menu,
        parse_mode="HTML",
    )
