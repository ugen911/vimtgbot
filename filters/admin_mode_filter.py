from aiogram.filters import BaseFilter
from aiogram.types import Message
from utils.admin_mode import is_admin_mode


class AdminModeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return is_admin_mode(message.from_user.id)


class NotAdminModeFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return not is_admin_mode(message.from_user.id)
