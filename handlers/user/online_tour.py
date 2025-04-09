import os
import json
import logging
from aiogram import Router, types, F
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS.get(SECTION_TITLE, "онлайнэкскурсии")
JSON_PATH = f"{DATA_DIR}/{SECTION_KEY}.json"
MEDIA_PATH = f"{MEDIA_DIR}/{SECTION_KEY}"

@router.message(F.text.lower().contains("онлайн экскурсия"))
async def show_online_tour(message: types.Message):
    logging.warning(f"[online_tour] Получено сообщение: {message.text!r}")

    if not os.path.exists(JSON_PATH):
        await message.answer("Онлайн-экскурсия пока недоступна.", reply_markup=back_menu)
        return

    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            blocks = json.load(f)
    except Exception as e:
        logging.error(f"[online_tour] Ошибка чтения JSON: {e}")
        await message.answer("⚠️ Не удалось загрузить экскурсию.", reply_markup=back_menu)
        return

    if not isinstance(blocks, list):
        await message.answer("⚠️ Неверный формат данных экскурсии.", reply_markup=back_menu)
        return

    for block in blocks:
        desc = block.get("desc", "")
        media_list = block.get("media", [])

        if media_list:
            for media_file in media_list:
                file_path = os.path.join(MEDIA_PATH, media_file)
                if os.path.exists(file_path):
                    if media_file.endswith(".mp4"):
                        await message.answer_video(
                            types.FSInputFile(file_path),
                            caption=desc,
                            parse_mode="HTML"
                        )
                    else:
                        await message.answer_photo(
                            types.FSInputFile(file_path),
                            caption=desc,
                            parse_mode="HTML"
                        )
                else:
                    await message.answer(
                        f"🕓 Видео <code>{media_file}</code> будет доступно позже:\n\n{desc}",
                        parse_mode="HTML",
                        reply_markup=back_menu
                    )
        else:
            await message.answer(desc, reply_markup=back_menu)

# Временный fallback, чтобы увидеть необработанные сообщения (можно удалить позже)
@router.message()
async def debug_message(message: types.Message):
    logging.warning(f"[debug fallback] Необработанное сообщение: {message.text!r}")
