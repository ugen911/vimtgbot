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


# Для обычных пользователей
@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_announcements(message: types.Message):
    if not os.path.exists(JSON_PATH):
        await message.answer("Пока нет анонсов.", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        await message.answer("Анонсы пока не опубликованы.", reply_markup=back_menu)
        return

    for item in items:
        text = f"<b>{item['title']}</b>\n{item['desc']}"
        media_files = item.get("media", [])

        if media_files:
            album = MediaGroupBuilder()
            for filename in media_files:
                full_path = os.path.join(MEDIA_PATH, filename)
                if filename.endswith(".mp4"):
                    album.add_video(
                        types.InputMediaVideo(media=types.FSInputFile(full_path))
                    )
                else:
                    album.add_photo(
                        types.InputMediaPhoto(media=types.FSInputFile(full_path))
                    )
            await message.answer_media_group(album.build())

        await message.answer(text, reply_markup=back_menu)


# Если пользователь в админ-режиме, он может увидеть управление анонсами
@router.message(F.text == "📰 Анонсы")
async def admin_announcements_redirect(message: types.Message):
    await message.answer("Открываю управление анонсами...")
    await message.bot.send_message(message.chat.id, "/admin_announcements")
