from aiogram import Router

# Заглушка для будущих админ-хендлеров
router = Router()

def register_admin_handlers(dp):
    dp.include_router(router)
