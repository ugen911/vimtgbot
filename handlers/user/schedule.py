import os
import json
from aiogram import Router, types, F
from aiogram.utils.media_group import MediaGroupBuilder
from config import DATA_DIR, MEDIA_DIR, SECTIONS
from keyboards.main_menu import back_menu
from filters.admin_mode_filter import AdminModeFilter, NotAdminModeFilter

router = Router()

SECTION_TITLE = "📅 Расписание занятий"
SECTION_KEY = SECTIONS.get(SECTION_TITLE, "расписание").strip()
JSON_PATH = os.path.join(DATA_DIR, f"{SECTION_KEY}.json")
MEDIA_PATH = os.path.join(MEDIA_DIR, SECTION_KEY)


@router.message(NotAdminModeFilter(), F.text == SECTION_TITLE)
async def choose_group(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="👶 Младшая группа")],
            [types.KeyboardButton(text="🧒 Старшая группа")],
            [types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите группу:", reply_markup=keyboard)


@router.message(
    NotAdminModeFilter(), F.text.in_(["👶 Младшая группа", "🧒 Старшая группа"])
)
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

    for block in blocks:
        desc = block.get("desc", "")
        media_list = block.get("media", [])

        album = MediaGroupBuilder()
        for media_file in media_list:
            file_path = os.path.join(MEDIA_PATH, group_key, media_file)
            if not os.path.exists(file_path):
                await message.answer(f"❌ Файл не найден: {media_file}")
                continue
            if media_file.endswith(".mp4"):
                file_size = os.path.getsize(file_path)
                if file_size <= 49 * 1024 * 1024:
                    album.add_video(types.FSInputFile(file_path))
                else:
                    await message.answer(
                        f"⚠️ Видео слишком большое (>50 МБ): {media_file}"
                    )
            else:
                album.add_photo(types.FSInputFile(file_path))

        built_album = album.build()
        if built_album:
            try:
                await message.answer_media_group(built_album)
            except Exception as e:
                await message.answer(f"⚠️ Ошибка при отправке медиа: {e}")

        if desc:
            await message.answer(desc, reply_markup=back_menu)

        await message.answer("────────────", reply_markup=back_menu)


@router.message(AdminModeFilter(), F.text == SECTION_TITLE)
async def admin_schedule_redirect(message: types.Message):
    await message.answer("Открываю управление расписанием...")
    await message.bot.send_message(message.chat.id, "/admin_schedule")
