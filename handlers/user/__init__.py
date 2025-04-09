from aiogram import Router
from . import services
from . import announcements
from . import excursion

def register_user_handlers(dp):
    dp.include_router(services.router)

def register_user_handlers(dp):
    dp.include_router(services.router)
    dp.include_router(announcements.router)

def register_user_handlers(dp):
    dp.include_router(services.router)
    dp.include_router(announcements.router)
    dp.include_router(excursion.router)