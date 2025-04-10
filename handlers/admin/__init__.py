from aiogram import Router
from . import admin_menu
from . import services_admin
from . import announcements_admin
from . import eat_admin
from . import schedule_admin
from . import pedagogues_admin
from . import online_tour_admin

router = Router()

router.include_router(admin_menu.router)
router.include_router(services_admin.router)
router.include_router(announcements_admin.router)
router.include_router(eat_admin.router)
router.include_router(schedule_admin.router)
router.include_router(pedagogues_admin.router)
router.include_router(online_tour_admin.router)
