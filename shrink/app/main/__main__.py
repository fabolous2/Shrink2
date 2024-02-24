import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.main.config import BOT_TOKEN
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider

from app.bot.handlers import commands, button_answers, pay_system, registration
from app.bot.callbacks import support, callbacks, email_list_action_calls, subscription_system_calls


async def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
                        )
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(scheduler=AsyncIOScheduler(timezone="Europe/Moscow"))
    dispatcher.include_routers(
        commands.commands_router,
        pay_system.router,
        registration.router,
        subscription_system_calls.router,
        support.router,
        callbacks.router,
        email_list_action_calls.router,
        button_answers.router
        )

    setup_dishka(providers=[DatabaseProvider(), DALProvider(), ServiceProvider()], router=dispatcher)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot, skip_updates=True)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
