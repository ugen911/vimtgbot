from aiogram import Router, types, F
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.media_group import MediaGroupBuilder
import os
import json
from keyboards.main_menu import main_menu, back_menu
from filters.admin_mode_filter import NotAdminModeFilter

router = Router()

# Главное меню для раздела "Педагоги"
pedagogues_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👩‍🏫 Воспитатели")],
        [KeyboardButton(text="🎓 Преподаватели")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
)


@router.message(NotAdminModeFilter(), F.text == "🧑‍🏫 Педагоги")
async def show_pedagogues_menu(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=pedagogues_menu)


async def send_pedagogues_list(
    message: types.Message, role_key: str, media_folder: str
):
    try:
        with open("data/pedagogues.json", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return await message.answer(
            "❌ Данные о педагогах не найдены.", reply_markup=back_menu
        )

    items = data.get(role_key, [])
    if not items:
        return await message.answer("Список пуст.", reply_markup=back_menu)

    for index, item in enumerate(items):
        name = item.get("name", "Без имени")
        role = item.get("role", "Роль не указана")
        description = item.get("description", "Описание отсутствует")
        media_list = item.get("media", [])

        text = f"<b>{name}</b>\n<b>{role}</b>\n{description}"
        await message.answer(text, parse_mode="HTML", reply_markup=back_menu)

        if media_list:
            album = MediaGroupBuilder()
            for file in media_list:
                file_path = os.path.join("media", media_folder, file)
                if not os.path.exists(file_path):
                    await message.answer(f"❌ Файл не найден: {file}")
                    continue
                if file.endswith(".mp4"):
                    album.add_video(FSInputFile(file_path))
                else:
                    album.add_photo(FSInputFile(file_path))

            built_album = album.build()
            if built_album:
                try:
                    await message.answer_media_group(built_album)
                except Exception as e:
                    await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")
        else:
            await message.answer("❌ Медиа не найдено.", reply_markup=back_menu)


@router.message(NotAdminModeFilter(), F.text == "👩‍🏫 Воспитатели")
async def show_vospitately(message: types.Message):
    await send_pedagogues_list(
        message, role_key="воспитатели", media_folder="воспитатели"
    )


@router.message(NotAdminModeFilter(), F.text == "🎓 Преподаватели")
async def show_prepodavateli(message: types.Message):
    await send_pedagogues_list(
        message, role_key="преподаватели", media_folder="преподаватели"
    )


@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
