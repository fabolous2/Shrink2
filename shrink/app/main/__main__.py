import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.main.config import BOT_TOKEN
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider

from app.bot.handlers.commands import commands_router
from app.bot.callbacks import support, callbacks, email_list_action_calls, subscription_system_calls


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(scheduler=AsyncIOScheduler(timezone="Europe/Moscow"))
    dispatcher.include_router(
        commands_router,
        subscription_system_calls.router,
        support.router,
        callbacks.router,
        email_list_action_calls.router
        )

    setup_dishka(providers=[DatabaseProvider(), DALProvider(), ServiceProvider()], router=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
