from aiogram import Dispatcher
from . import (
    admin_menu,
    services_admin,
    announcements_admin,
    eat_admin,
    schedule_admin,
    pedagogues_admin,
    pedagogues_admin_add,
    pedagogues_admin_edit,
    pedagogues_admin_delete,
    online_tour_admin,
    admin_manage,
)


def register_admin_handlers(dp: Dispatcher):
    dp.include_router(admin_menu.router)
    dp.include_router(services_admin.router)
    dp.include_router(announcements_admin.router)
    dp.include_router(eat_admin.router)
    dp.include_router(schedule_admin.router)

    # педагоги
    dp.include_router(pedagogues_admin.router)
    dp.include_router(pedagogues_admin_add.router)
    dp.include_router(pedagogues_admin_edit.router)
    dp.include_router(pedagogues_admin_delete.router)

    dp.include_router(online_tour_admin.router)
    dp.include_router(admin_manage.router)
