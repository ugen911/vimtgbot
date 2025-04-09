import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import main_menu, back_menu
from keyboards.services_menu import services_menu

router = Router()

SECTION_TITLE = "📚 Услуги"
SECTION_KEY = SECTIONS[SECTION_TITLE]
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"

@router.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "🏡 <b>Добро пожаловать в детский сад \"Виммельбух\"! 👶</b>\n\n"
        "Выберите интересующий раздел из меню ниже:",
        reply_markup=main_menu
    )

# Главное меню
@router.message(F.text == "🏠 Главное меню")
async def go_home(message: types.Message):
    await message.answer("🏡 Главное меню:", reply_markup=main_menu)

# Назад — тоже ведёт в главное меню
@router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("🔙 Возвращаемся назад:", reply_markup=main_menu)

# При нажатии на "📚 Услуги" — открываем подменю
@router.message(F.text == SECTION_TITLE)
async def show_services_menu(message: types.Message):
    await message.answer("Выберите услугу:", reply_markup=services_menu)

# Обработка выбора конкретной услуги
@router.message(F.text.in_([
    "🏫 Детский сад полного дня", "🗣 Логопед", "🎤 Запуск речи",
    "💆 Логомассаж", "🧘 Аэройога", "🧠 Подготовка к школе",
    "📚 Скорочтение", "🎨 Творческая мастерская", "🧮 Ментальная арифметика",
    "👩‍👧 Вместе с мамой", "💪 Крепыш ОФП", "🎵 Музыкальная терапия"
]))
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
                album.add_video(types.InputMediaVideo(media=types.FSInputFile(full_path)))
            else:
                album.add_photo(types.InputMediaPhoto(media=types.FSInputFile(full_path)))
        await message.answer_media_group(album.build())

    await message.answer(text, reply_markup=services_menu)
