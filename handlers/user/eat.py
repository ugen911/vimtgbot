from aiogram import Router, types, F
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile,
    InputMediaPhoto,
    InputMediaVideo,
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


# Обработчик кнопки "Меню" для обычных пользователей (когда они не в админ-режиме)
@router.message(NotAdminModeFilter(), F.text == "🍎 Меню")
async def show_menu(message: types.Message):
    try:
        with open("data/menu.json", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return await message.answer("❌ Меню пока недоступно.", reply_markup=back_menu)

    menu_items = data.get("menu_items", [])

    for item in menu_items:
        name = item["name"]
        description = item["description"]
        media_list = item.get("media", [])

        message_text = f"<b>{name}</b>\n{description}"
        await message.answer(message_text, parse_mode="HTML", reply_markup=back_menu)

        if media_list:
            album = MediaGroupBuilder()
            for media_file in media_list:
                file_path = os.path.join("media", "меню", media_file)
                if os.path.exists(file_path):
                    if media_file.endswith(".mp4"):
                        album.add_video(FSInputFile(file_path))
                    else:
                        album.add_photo(FSInputFile(file_path))
            built_album = album.build()
            if built_album:
                await message.answer_media_group(built_album)
            else:
                await message.answer("⚠️ Медиафайлы не найдены.", reply_markup=back_menu)
        else:
            await message.answer("❌ Медиа не найдено.", reply_markup=back_menu)


# Обработчик для приема фото и видео (когда пользователь отправляет вложения)
@router.message(F.content_type.in_(["photo", "video"]))
async def handle_media(message: types.Message):
    if message.photo:
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        await message.answer(
            f"Фото получено! Путь к файлу: {file_path}", reply_markup=main_menu
        )

    elif message.video:
        file_id = message.video.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        await message.answer(
            f"Видео получено! Путь к файлу: {file_path}", reply_markup=main_menu
        )


# Кнопка "Назад" для возврата в главное меню
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
