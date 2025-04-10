import os
import json
from aiogram import Bot
from uuid import uuid4


def load_json(path):
    if not os.path.exists(path):
        return [] if path.endswith(".json") else {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


async def save_media_file(
    bot: Bot, file_id: str, media_dir: str, is_video=False
) -> str:
    ensure_dir(media_dir)
    ext = ".mp4" if is_video else ".jpg"
    filename = f"{uuid4().hex}{ext}"
    full_path = os.path.join(media_dir, filename)

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, full_path)

    return filename
