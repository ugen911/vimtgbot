from aiogram import Router, F, types
from config import ADMINS
from utils.admin_mode import enable_admin, disable_admin, is_admin_mode

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


# Главное меню (показывается одинаково для всех)
async def show_admin_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="📚 Услуги"),
                types.KeyboardButton(text="📰 Анонсы"),
            ],
            [
                types.KeyboardButton(text="🍎 Меню"),
                types.KeyboardButton(text="📅 Расписание"),
            ],
            [
                types.KeyboardButton(text="🧑‍🏫 Педагоги"),
                types.KeyboardButton(text="🌐 Онлайн экскурсия"),
            ],
        ],
        resize_keyboard=True,
    )
    await message.answer("🏡 Главное меню:", reply_markup=keyboard)


# Обработка кнопок, перенаправление зависит от режима
@router.message(F.text == "📚 Услуги")
async def handle_services(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю управление услугами...")
        await message.bot.send_message(message.chat.id, "/admin_services")
    else:
        await message.bot.send_message(message.chat.id, "📚 Услуги")


@router.message(F.text == "📰 Анонсы")
async def handle_announcements(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю управление анонсами...")
        await message.bot.send_message(message.chat.id, "/admin_announcements")
    else:
        await message.bot.send_message(message.chat.id, "📰 Анонсы")


@router.message(F.text == "🍎 Меню")
async def handle_menu(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю меню питания...")
        await message.bot.send_message(message.chat.id, "/admin_menu")
    else:
        await message.bot.send_message(message.chat.id, "🍎 Меню")


@router.message(F.text == "📅 Расписание")
async def handle_schedule(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю расписание...")
        await message.bot.send_message(message.chat.id, "/admin_schedule")
    else:
        await message.bot.send_message(message.chat.id, "📅 Расписание")


@router.message(F.text == "🧑‍🏫 Педагоги")
async def handle_pedagogues(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю педагогов...")
        await message.bot.send_message(message.chat.id, "/admin_pedagogues")
    else:
        await message.bot.send_message(message.chat.id, "🧑‍🏫 Педагоги")


@router.message(F.text == "🌐 Онлайн экскурсия")
async def handle_online_tour(message: types.Message):
    if is_admin_mode(message.from_user.id):
        await message.answer("Открываю онлайн-экскурсии...")
        await message.bot.send_message(message.chat.id, "/admin_online")
    else:
        await message.bot.send_message(message.chat.id, "🌐 Онлайн экскурсия")
