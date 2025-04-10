from aiogram import Router, F, types
from config import ADMINS

router = Router()


@router.message(F.text == "/admin")
async def show_admin_menu(message: types.Message):
    if message.from_user.id not in ADMINS:
        return await message.answer("⛔ У вас нет доступа к админ-панели")

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
    await message.answer("👩‍💻 Админ-панель:", reply_markup=keyboard)


# перенаправление на соответствующие команды
@router.message(F.text == "📚 Услуги")
async def admin_services_redirect(message: types.Message):
    await message.answer("Открываю управление услугами...")
    await message.bot.send_message(message.chat.id, "/admin_services")


@router.message(F.text == "📰 Анонсы")
async def admin_announcements_redirect(message: types.Message):
    await message.answer("Открываю управление анонсами...")
    await message.bot.send_message(message.chat.id, "/admin_announcements")


@router.message(F.text == "🍎 Меню")
async def admin_menu_redirect(message: types.Message):
    await message.answer("Открываю меню питания...")
    await message.bot.send_message(message.chat.id, "/admin_menu")


@router.message(F.text == "📅 Расписание")
async def admin_schedule_redirect(message: types.Message):
    await message.answer("Открываю расписание...")
    await message.bot.send_message(message.chat.id, "/admin_schedule")


@router.message(F.text == "🧑‍🏫 Педагоги")
async def admin_pedagogues_redirect(message: types.Message):
    await message.answer("Открываю педагогов...")
    await message.bot.send_message(message.chat.id, "/admin_pedagogues")


@router.message(F.text == "🌐 Онлайн экскурсия")
async def admin_online_tour_redirect(message: types.Message):
    await message.answer("Открываю онлайн-экскурсию...")
    await message.bot.send_message(message.chat.id, "/admin_online")

