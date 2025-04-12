import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu, main_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_services_menu(message: types.Message):
    if not os.path.exists(JSON_PATH):
        await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)
        return

    buttons = [
        [types.KeyboardButton(text=item["title"])] for item in items if "title" in item
    ]
    buttons += [[types.KeyboardButton(text="🔙 Назад")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer("Выберите услугу:", reply_markup=keyboard)


@router.message(
    NotAdminModeFilter(),
    F.text.in_(
        [
            item["title"]
            for item in json.load(open(JSON_PATH, encoding="utf-8"))
            if isinstance(item, dict) and "title" in item
        ]
    ),
)
async def show_service_detail(message: types.Message):
    if not os.path.exists(JSON_PATH):
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    service = next(
        (item for item in items if item.get("title") == message.text.strip()), None
    )

    if not service:
        return

    desc = service.get("desc", "")
    media_files = service.get("media", [])

    if media_files:
        album = MediaGroupBuilder()
        send_as_album = True

        for filename in media_files:
            file_path = os.path.join(MEDIA_PATH, filename)
            if not os.path.exists(file_path):
                await message.answer(f"❌ Файл не найден: {filename}")
                continue

            if filename.endswith(".mp4"):
                file_size = os.path.getsize(file_path)
                if file_size <= 49 * 1024 * 1024:
                    album.add_video(types.FSInputFile(file_path))
                else:
                    send_as_album = False
                    break
            else:
                album.add_photo(types.FSInputFile(file_path))

        if send_as_album and album.build():
            try:
                await message.answer_media_group(album.build())
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")
        else:
            for filename in media_files:
                file_path = os.path.join(MEDIA_PATH, filename)
                if not os.path.exists(file_path):
                    continue
                if filename.endswith(".mp4"):
                    await message.answer_video(types.FSInputFile(file_path))
                else:
                    await message.answer_photo(types.FSInputFile(file_path))

    text = f"<b>{service['title']}</b>\n{desc}"
    await message.answer(text, parse_mode="HTML", reply_markup=back_menu)


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)


@router.message(F.text == "🏠 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏠 Главное меню:", reply_markup=main_menu)
