from aiogram import Router, types, F
from keyboards.main_menu import main_menu, back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()


# Контакты (доступно только если пользователь не в админ-режиме)
@router.message(NotAdminModeFilter(), F.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    contact_info = (
        "<b>📞 Контакты:</b>\n\n"
        "Телефон: <b>215-42-13</b>\n"
        "WhatsApp/Telegram: <b>+7 (923) 281-19-83</b>\n"
        "\nДля связи в мессенджерах напишите нам на этот номер!"
    )
    await message.answer(contact_info, parse_mode="HTML", reply_markup=back_menu)


# Главное меню
@router.message(F.text == "📺 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏡 Главное меню:", reply_markup=main_menu)
