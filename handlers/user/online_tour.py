import os
import json
from aiogram import Router, types, F
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu

router = Router()

SECTION_TITLE = "🌐 Онлайн экскурсия"
SECTION_KEY = SECTIONS[SECTION_TITLE].strip()
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(F.text == SECTION_TITLE)
async def show_online_tour(message: types.Message):

    if not os.path.exists(JSON_PATH):
        await message.answer(
            "Онлайн-экскурсия пока недоступна.", reply_markup=back_menu
        )
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        blocks = json.load(f)

    if not isinstance(blocks, list):
        await message.answer(
            "⚠️ Неверный формат данных экскурсии.", reply_markup=back_menu
        )
        return


    for i, block in enumerate(blocks):
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
                            parse_mode="HTML",
                        )
                    else:
                        await message.answer_photo(
                            types.FSInputFile(file_path),
                            caption=desc,
                            parse_mode="HTML",
                        )
                else:
                    await message.answer(
                        f"❌ Видео будет доступно позже:\n\n{desc}",
                        reply_markup=back_menu,
                    )
        else:
            await message.answer(desc, reply_markup=back_menu)
