from typing import Dict, Any
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from apscheduler_di import ContextSchedulerDecorator


class SchedulerMiddleware(LifetimeControllerMiddleware):

    def __init__(self, scheduler: ContextSchedulerDecorator):
        super().__init__()
        self._scheduler = scheduler

    async def pre_process(self, obj: TelegramObject, data: Dict[str, Any], *args: Any):
        data["scheduler"] = self._scheduler
