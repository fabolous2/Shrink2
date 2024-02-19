from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka

from app.main.config import BOT_TOKEN
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider

from app.bot.handlers.commands import commands_router


def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher()
    dispatcher.include_router(commands_router)

    setup_dishka(providers=[DatabaseProvider(), DALProvider(), ServiceProvider()], router=dispatcher)

    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
