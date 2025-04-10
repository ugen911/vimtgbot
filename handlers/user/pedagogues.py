from aiogram import Router, types, F
import os
import json
from keyboards.main_menu import main_menu, back_menu
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

router = Router()

pedagogues_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👩‍🏫 Воспитатели")],
        [KeyboardButton(text="🎓 Преподаватели")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
)

# Обработчик кнопки "Педагоги" — выводит меню выбора
@router.message(F.text == "🧑‍🏫 Педагоги")
async def show_pedagogues_menu(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=pedagogues_menu)


@router.message(F.text == "👩‍🏫 Воспитатели")
async def show_vospitately(message: types.Message):
    # Загружаем данные о воспитателях из JSON
    with open("data/pedagogues.json", encoding="utf-8") as f:
        data = json.load(f)

    # Получаем информацию о воспитателях
    vospitately = data.get("воспитатели", [])

    # Формируем и отправляем сообщение для каждого воспитателя
    for vospitately_info in vospitately:
        name = vospitately_info["name"]
        role = vospitately_info["role"]
        description = vospitately_info["description"]
        media_list = vospitately_info.get("media", [])

        message_text = f"<b>{name}</b>\n{role}\n{description}"
        await message.answer(message_text, parse_mode="HTML", reply_markup=back_menu)

        # Отправляем медиа (фото и видео)
        if not media_list:
            await message.answer("❌ Медиа не найдено.", reply_markup=back_menu)
        else:
            for media_file in media_list:
                file_path = os.path.join("media", "воспитатели", media_file)
                if os.path.exists(file_path):
                    if media_file.endswith(".mp4"):
                        await message.answer_video(types.FSInputFile(file_path))
                    else:
                        await message.answer_photo(types.FSInputFile(file_path))
                else:
                    await message.answer(
                        f"❌ Файл не найден: {media_file}", reply_markup=back_menu
                    )


@router.message(F.text == "🎓 Преподаватели")
async def show_prepodavateli(message: types.Message):
    # Загружаем данные о преподавателях из JSON
    with open("data/pedagogues.json", encoding="utf-8") as f:
        data = json.load(f)

    # Получаем информацию о преподавателях
    prepodavateli = data.get("преподаватели", [])

    # Формируем и отправляем сообщение для каждого преподавателя
    for prepodavatel_info in prepodavateli:
        name = prepodavatel_info["name"]
        role = prepodavatel_info["role"]
        description = prepodavatel_info["description"]
        media_list = prepodavatel_info.get("media", [])

        message_text = f"<b>{name}</b>\n{role}\n{description}"
        await message.answer(message_text, parse_mode="HTML", reply_markup=back_menu)

        # Отправляем медиа (фото и видео)
        if not media_list:
            await message.answer("❌ Медиа не найдено.", reply_markup=back_menu)
        else:
            for media_file in media_list:
                file_path = os.path.join("media", "преподаватели", media_file)
                if os.path.exists(file_path):
                    if media_file.endswith(".mp4"):
                        await message.answer_video(types.FSInputFile(file_path))
                    else:
                        await message.answer_photo(types.FSInputFile(file_path))
                else:
                    await message.answer(
                        f"❌ Файл не найден: {media_file}", reply_markup=back_menu
                    )


# Кнопка "Назад" для возврата в главное меню
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню.", reply_markup=main_menu)
