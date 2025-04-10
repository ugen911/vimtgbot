import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import main_menu, back_menu

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"



@router.message(F.text == SECTION_TITLE)
async def show_services_menu(message: types.Message):
    if not os.path.exists(JSON_PATH):
        await message.answer("❌ Услуги не найдены.", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    if not items:
        await message.answer("Список услуг пока пуст.", reply_markup=back_menu)
        return

    # Формируем клавиатуру динамически
    buttons = [[types.KeyboardButton(text=item["title"])] for item in items]
    buttons += [
        [types.KeyboardButton(text="🔙 Назад")],
        [types.KeyboardButton(text="🏠 Главное меню")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer("Выберите услугу:", reply_markup=keyboard)


@router.message(
    F.text.in_(
        [
            item["title"]
            for item in json.load(
                open(JSON_PATH, encoding="utf-8")
            )  # список всех названий услуг
            if isinstance(item, dict) and "title" in item
        ]
    )
)
async def show_service_detail(message: types.Message):
    service_name = message.text.strip()
    if not os.path.exists(JSON_PATH):
        await message.answer("❌ Услуги не найдены.", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        items = json.load(f)

    service = next((item for item in items if item["title"] == service_name), None)

    if not service:
        await message.answer("⚠️ Информация пока недоступна.", reply_markup=back_menu)
        return

    text = f"<b>{service['title']}</b>\n{service['desc']}"
    media_files = service.get("media", [])

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


@router.message(F.text.in_(["🔙 Назад", "🏠 Главное меню"]))
async def go_back(message: types.Message):
    await message.answer("🏡 Главное меню:", reply_markup=main_menu)
