from aiogram.filters import BaseFilter
from aiogram.types import Message
from config import ADMINS


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMINS


class IsNotAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id not in ADMINS
