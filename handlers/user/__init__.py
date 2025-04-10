from aiogram import Router
from . import services
from . import announcements
from . import excursion
from . import online_tour


def register_user_handlers(dp):
    print("👉 Регистрируем пользовательские роутеры...")
    from . import online_tour, services, announcements, excursion

    dp.include_router(online_tour.router)
    print("✅ router online_tour зарегистрирован")

    dp.include_router(services.router)
    dp.include_router(announcements.router)
    dp.include_router(excursion.router)
