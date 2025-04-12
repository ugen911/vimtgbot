from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
import os
import json
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu, main_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE].strip()
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def show_online_tour(message: types.Message):
    if not os.path.exists(JSON_PATH):
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    with open(JSON_PATH, encoding="utf-8") as f:
        blocks = json.load(f)

    if not isinstance(blocks, list) or not blocks:
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    for block in blocks:
        desc = block.get("desc", "")
        media_files = block.get("media", [])

        if media_files:
            album = MediaGroupBuilder()
            send_as_album = True

            for file in media_files:
                file_path = os.path.join(MEDIA_PATH, file)
                if not os.path.exists(file_path):
                    continue
                if file.endswith(".mp4"):
                    file_size = os.path.getsize(file_path)
                    if file_size <= 49 * 1024 * 1024:
                        album.add_video(FSInputFile(file_path))
                    else:
                        send_as_album = False
                        break
                else:
                    album.add_photo(FSInputFile(file_path))

            if send_as_album and album.build():
                try:
                    await message.answer_media_group(album.build())
                except Exception as e:
                    await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")
            else:
                for file in media_files:
                    file_path = os.path.join(MEDIA_PATH, file)
                    if not os.path.exists(file_path):
                        continue
                    if file.endswith(".mp4"):
                        await message.answer_video(FSInputFile(file_path))
                    else:
                        await message.answer_photo(FSInputFile(file_path))

        if desc:
            await message.answer(desc, parse_mode="HTML", reply_markup=back_menu)


@router.message(F.text == SECTION_TITLE)
async def admin_online_tour_redirect(message: types.Message):
    await message.answer("Открываю управление онлайн-экскурсиями...")
    await message.bot.send_message(message.chat.id, "/admin_online")


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)


@router.message(F.text == "🏠 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏠 Главное меню:", reply_markup=main_menu)
