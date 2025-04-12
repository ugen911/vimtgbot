from aiogram import Router, F, types
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

# Клавиатура для меню питания
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍽 Меню дня")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
)


@router.message(NotAdminModeFilter(), F.text == "🍎 Меню")
async def show_menu(message: types.Message):
    try:
        with open("data/menu.json", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return await message.answer("🛠 Мы над этим работаем...", reply_markup=back_menu)

    menu_items = data.get("menu_items", [])
    if not isinstance(menu_items, list) or not menu_items:
        return await message.answer("🛠 Меню пока недоступно.", reply_markup=back_menu)

    for item in menu_items:
        name = item.get("name", "Меню")
        description = item.get("description", "")
        media_list = item.get("media", [])

        files_exist = False
        album = MediaGroupBuilder()

        # Проверим все медиа
        for media_file in media_list:
            file_path = os.path.join(
                "media", "menu", media_file
            )  # 🔧 если media/меню, поменяй тут
            if not os.path.isfile(file_path):
                await message.answer(f"⚠️ Файл не найден: {media_file}")
                continue

            files_exist = True
            if media_file.endswith(".mp4"):
                if os.path.getsize(file_path) <= 49 * 1024 * 1024:
                    album.add_video(FSInputFile(file_path))
            else:
                album.add_photo(FSInputFile(file_path))

        # Отправка медиа
        if files_exist and album.build():
            try:
                await message.answer_media_group(album.build())
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке альбома: {e}")
        elif files_exist:
            # fallback по одному
            for media_file in media_list:
                file_path = os.path.join("media", "menu", media_file)
                if not os.path.isfile(file_path):
                    continue
                if media_file.endswith(".mp4"):
                    await message.answer_video(FSInputFile(file_path))
                else:
                    await message.answer_photo(FSInputFile(file_path))
        else:
            await message.answer(
                "❌ Нет доступных медиафайлов.", reply_markup=back_menu
            )

        # Текстовое описание блока
        await message.answer(
            f"<b>{name}</b>\n{description}", parse_mode="HTML", reply_markup=back_menu
        )


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
