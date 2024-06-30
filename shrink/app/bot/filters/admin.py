from aiogram.types import Message
from aiogram.filters import Filter

class AdminProtect(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [6384960822, 6644596826, 805435552]
