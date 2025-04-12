import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import main_menu, back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

SECTION_TITLE = "📰 Анонсы"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_announcements(message: types.Message):
    if not os.path.exists(JSON_PATH):
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    for item in items:
        title = item.get("title", "Без заголовка")
        desc = item.get("desc", "")
        media_files = item.get("media", [])
        text = f"<b>{title}</b>\n{desc}"

        if media_files:
            album = MediaGroupBuilder()
            for filename in media_files:
                full_path = os.path.join(MEDIA_PATH, filename)
                if not os.path.exists(full_path):
                    await message.answer(f"⚠️ Файл не найден: {filename}")
                    continue

                if filename.endswith(".mp4"):
                    file_size = os.path.getsize(full_path)
                    if file_size <= 49 * 1024 * 1024:
                        album.add_video(types.FSInputFile(full_path))
                    else:
                        await message.answer(
                            f"⚠️ Видео слишком большое (>50 МБ): {filename}"
                        )
                else:
                    album.add_photo(types.FSInputFile(full_path))

            try:
                await message.answer_media_group(album.build())
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")

        await message.answer(text, reply_markup=back_menu)


@router.message(F.text == "📰 Анонсы")
async def admin_announcements_redirect(message: types.Message):
    await message.answer("Открываю управление анонсами...")
    await message.bot.send_message(message.chat.id, "/admin_announcements")


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)


@router.message(F.text == "🏠 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏠 Главное меню:", reply_markup=main_menu)
