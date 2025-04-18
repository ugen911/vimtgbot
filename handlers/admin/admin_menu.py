from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from config import ADMINS
from utils.admin_mode import enable_admin, disable_admin
from filters.admin_mode_filter import AdminModeFilter
from keyboards.main_menu import admin_main_menu  # ✅ импорт единого меню

router = Router()


# Команда для включения режима администратора
@router.message(F.text == "/admin")
async def enter_admin_mode(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ У вас нет доступа к админке")
    enable_admin(message.from_user.id)
    await message.answer("🔐 Режим администратора включён")
    await show_admin_menu(message)


# Команда для выхода из режима администратора
@router.message(F.text == "/exit_admin")
async def exit_admin_mode(message: types.Message):
    disable_admin(message.from_user.id)
    await message.answer("👤 Режим администратора отключён")


# Главное меню администратора
async def show_admin_menu(message: types.Message):
    await message.answer("🏡 Главное меню:", reply_markup=admin_main_menu)


# Навигация по разделам
@router.message(AdminModeFilter(), F.text == "📚 Услуги")
async def admin_services_redirect(message: types.Message):
    await message.answer("Открываю управление услугами...")
    await message.bot.send_message(message.chat.id, "/admin_services")


@router.message(AdminModeFilter(), F.text == "📰 Анонсы")
async def admin_announcements_redirect(message: types.Message):
    await message.answer("Открываю управление анонсами...")
    await message.bot.send_message(message.chat.id, "/admin_announcements")


@router.message(AdminModeFilter(), F.text == "🍎 Меню")
async def admin_menu_redirect(message: types.Message):
    await message.answer("Открываю меню питания...")
    await message.bot.send_message(message.chat.id, "/admin_menu")


@router.message(AdminModeFilter(), F.text == "📅 Расписание")
async def admin_schedule_redirect(message: types.Message):
    await message.answer("Открываю расписание...")
    await message.bot.send_message(message.chat.id, "/admin_schedule")


@router.message(AdminModeFilter(), F.text == "🧑‍🏫 Педагоги")
async def admin_pedagogues_redirect(message: types.Message):
    await message.answer("Открываю педагогов...")
    await message.bot.send_message(message.chat.id, "/admin_pedagogues")


@router.message(AdminModeFilter(), F.text == "🌐 Онлайн экскурсия")
async def admin_online_tour_redirect(message: types.Message):
    await message.answer("Открываю онлайн-экскурсию...")
    await message.bot.send_message(message.chat.id, "/admin_online")


# Универсальная кнопка "Назад" в админке
@router.message(AdminModeFilter(), F.text == "🔙 Назад")
async def back_to_admin_main(message: types.Message, state: FSMContext):
    await state.clear()
    await show_admin_menu(message)
