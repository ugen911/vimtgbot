import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_services_menu(message: types.Message):
    if not os.path.exists(JSON_PATH):
        await message.answer("❌ Услуги не найдены.", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        await message.answer("Список услуг пока пуст.", reply_markup=back_menu)
        return

    buttons = [[types.KeyboardButton(text=item["title"])] for item in items]
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
    service_name = message.text.strip()

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    service = next((item for item in items if item["title"] == service_name), None)

    if not service:
        return await message.answer("⚠️ Информация об услуге не найдена.")

    desc = service.get("desc", "")
    media_files = service.get("media", [])

    album = MediaGroupBuilder()
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
                await message.answer(f"⚠️ Видео слишком большое (>50 МБ): {filename}")
        else:
            album.add_photo(types.FSInputFile(file_path))

    if built_album := album.build():
        try:
            await message.answer_media_group(built_album)
        except Exception as e:
            await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")

    text = f"<b>{service['title']}</b>\n{desc}"
    await message.answer(text, parse_mode="HTML", reply_markup=back_menu)
