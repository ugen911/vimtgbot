from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
)
import os
import json
from aiogram.utils.media_group import MediaGroupBuilder
from keyboards.main_menu import main_menu, back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

# Главное меню для раздела "Меню"
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🍽 Меню дня")], [KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True,
)


@router.message(NotAdminModeFilter(), F.text == "🍎 Меню")
async def show_menu(message: types.Message):
    try:
        with open("data/menu.json", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    menu_items = data.get("menu_items", [])

    if not menu_items:
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    for item in menu_items:
        name = item.get("name", "Без названия")
        description = item.get("description", "")
        media_list = item.get("media", [])

        if media_list:
            album = MediaGroupBuilder()
            send_as_album = True

            for media_file in media_list:
                file_path = os.path.join("media", "меню", media_file)
                if not os.path.exists(file_path):
                    await message.answer(f"⚠️ Файл не найден: {media_file}")
                    continue

                if media_file.endswith(".mp4"):
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
                for media_file in media_list:
                    file_path = os.path.join("media", "меню", media_file)
                    if not os.path.exists(file_path):
                        continue
                    if media_file.endswith(".mp4"):
                        await message.answer_video(FSInputFile(file_path))
                    else:
                        await message.answer_photo(FSInputFile(file_path))
        else:
            await message.answer("❌ Медиа не найдено.", reply_markup=back_menu)

        message_text = f"<b>{name}</b>\n{description}"
        await message.answer(message_text, parse_mode="HTML", reply_markup=back_menu)


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
