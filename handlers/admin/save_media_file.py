import os
import uuid
import asyncio
from io import BytesIO
from PIL import Image
from aiogram import Bot
from aiogram.types import FSInputFile


async def save_media_file(bot: Bot, file_id: str, save_dir: str, is_video=False) -> str:
    file = await bot.get_file(file_id)
    file_path = file.file_path

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    raw_name = f"{uuid.uuid4().hex}"
    if is_video:
        # Step 1: download original video
        temp_input = os.path.join(save_dir, f"{raw_name}_orig.mp4")
        with open(temp_input, "wb") as f:
            await bot.download_file(file_path, destination=f)

        # Step 2: compress video with ffmpeg
        output_path = os.path.join(save_dir, f"{raw_name}.mp4")
        command = [
            "ffmpeg",
            "-i",
            temp_input,
            "-vf",
            "scale='min(1280,iw)':-2",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "28",
            "-c:a",
            "aac",
            "-y",
            output_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.communicate()

        os.remove(temp_input)
        return os.path.basename(output_path)

    else:
        # Step 1: download photo to memory
        bio = BytesIO()
        await bot.download_file(file_path, destination=bio)
        bio.seek(0)

        # Step 2: compress and save JPEG
        img = Image.open(bio)
        img = img.convert("RGB")
        img.thumbnail((1280, 1280))

        filename = f"{raw_name}.jpg"
        output_path = os.path.join(save_dir, filename)
        img.save(output_path, "JPEG", quality=80)

        return filename
