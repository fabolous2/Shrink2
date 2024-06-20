from aiogram.types import Message
from aiogram.filters import Filter

class AdminProtect(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in [6644596826, 5297779345, 805435552]
