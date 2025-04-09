from aiogram import Router
from . import services
from . import announcements
from . import excursion
from . import online_tour

def register_user_handlers(dp):
    dp.include_router(services.router)
    dp.include_router(announcements.router)
    dp.include_router(excursion.router)
    dp.include_router(online_tour.router)