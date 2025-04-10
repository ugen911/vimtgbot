import os
import json
from aiogram import Router, types, F
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu
from handlers.user.state import user_states

router = Router()

SECTION_TITLE = "📅 Расписание занятий"
SECTION_KEY = SECTIONS.get(
    SECTION_TITLE, "расписание"
).strip()  # 👈 безопасное извлечение ключа
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(F.text == SECTION_TITLE)
async def choose_group(message: types.Message):
    user_states.pop(message.from_user.id, None)  # 👈 сброс состояния формы

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👶 Младшая группа")],
            [types.KeyboardButton(text="🧒 Старшая группа")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу:", reply_markup=keyboard)


@router.message(F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"]))
async def show_schedule(message: types.Message):
    group_key = "младшая" if "Младшая" in message.text else "старшая"

    if not os.path.exists(JSON_PATH):
        await message.answer("Расписание пока недоступно.", reply_markup=back_menu)
        return

    with open(JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    blocks = data.get(group_key, [])
    if not isinstance(blocks, list):
        await message.answer(
            "⚠️ Неверный формат данных расписания.", reply_markup=back_menu
        )
        return


    for i, block in enumerate(blocks):
        desc = block.get("desc", "")
        media_list = block.get("media", [])


        if media_list:
            for media_file in media_list:
                file_path = os.path.join(MEDIA_PATH, group_key, media_file)
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
                        f"❌ Файл не найден: {media_file}\n{desc}",
                        reply_markup=back_menu,
                    )
        else:
            await message.answer(desc, reply_markup=back_menu)
