import os
import asyncio
import logging  # ← добавили
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from config import TOKEN
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers

logging.basicConfig(level=logging.INFO)  # ← ВАЖНО!

load_dotenv()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


register_admin_handlers(dp)
register_user_handlers(dp)


async def main():
    print("🤖 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
