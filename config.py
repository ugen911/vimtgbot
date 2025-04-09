import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Пути
DATA_DIR = "data"
MEDIA_DIR = "media"

# ID или username администраторов
ADMINS = ["Natali_stro", "TUSHC"]

# Названия секций и соответствующие JSON-файлы/папки
SECTIONS = {
    "📚 Услуги": "услуги",
    "📰 Анонсы": "анонсы",
    "🧑‍🏫 Педагоги": "педагоги",
    "📆 Расписание занятий": "расписание",
    "🍎 Меню": "меню",
    "📋 Запись на экскурсию": "экскурсии",
    "🌐 Онлайн экскурсия": "онлайнэкскурсии"
}
