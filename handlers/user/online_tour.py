from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
import os
import json
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE].strip()
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_online_tour(message: types.Message):
    if not os.path.exists(JSON_PATH):
        return await message.answer(
            "Онлайн-экскурсия пока недоступна.", reply_markup=back_menu
        )

    with open(JSON_PATH, encoding="utf-8") as f:
        blocks = json.load(f)

    if not isinstance(blocks, list) or not blocks:
        return await message.answer("Альбомы ещё не загружены.", reply_markup=back_menu)

    for i, block in enumerate(blocks):
        desc = block.get("desc", "")
        media_files = block.get("media", [])

        if media_files:
            album = MediaGroupBuilder()
            for file in media_files:
                file_path = os.path.join(MEDIA_PATH, file)
                if not os.path.exists(file_path):
                    continue
                if file.endswith(".mp4"):
                    album.add_video(FSInputFile(file_path))
                else:
                    album.add_photo(FSInputFile(file_path))

            try:
                await message.answer_media_group(album.build())
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке альбома: {e}")

        await message.answer(desc, parse_mode="HTML", reply_markup=back_menu)


@router.message(F.text == SECTION_TITLE)
async def admin_online_tour_redirect(message: types.Message):
    await message.answer("Открываю управление онлайн-экскурсиями...")
    await message.bot.send_message(message.chat.id, "/admin_online")
