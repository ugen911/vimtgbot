from aiogram import Router
from . import services
from . import announcements
from . import online_tour
from . import schedule
from . import excursion
from . import pedagogues


def register_user_handlers(dp):
    print("👉 Регистрируем пользовательские роутеры...")
    dp.include_router(online_tour.router)
    print("✅ router online_tour зарегистрирован")
    dp.include_router(services.router)
    dp.include_router(announcements.router)
    dp.include_router(schedule.router)
    dp.include_router(excursion.router)
    dp.include_router(pedagogues.router)
