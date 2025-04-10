from aiogram import Router
from . import services
from . import announcements
from . import online_tour
from . import schedule
from . import excursion
from . import pedagogues
from . import eat
from . import auto_start  # добавь


def register_user_handlers(dp):
    ...
    dp.include_router(auto_start.router)  # добавь в самый конец


def register_user_handlers(dp):
    dp.include_router(online_tour.router)
    dp.include_router(services.router)
    dp.include_router(announcements.router)
    dp.include_router(schedule.router)
    dp.include_router(excursion.router)
    dp.include_router(pedagogues.router)
    dp.include_router(eat.router)
    dp.include_router(auto_start.router)
