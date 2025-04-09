from aiogram import Router
from . import services

def register_user_handlers(dp):
    dp.include_router(services.router)
