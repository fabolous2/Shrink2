import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from dishka.integrations.aiogram import setup_dishka
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.main.config import BOT_TOKEN
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider
from app.bot.handlers import commands, button_answers, pay_system, registration, mailing
from app.bot.callbacks import support, callbacks, email_list_action_calls, subscription_system_calls, audio_list_calls
from app.bot.middlewares.album_middleware import TTLCacheAlbumMiddleware
from app.bot.middlewares.chat_actions_middleware import MailChatActionMiddleware
from apscheduler_di import ContextSchedulerDecorator

logger = logging.getLogger(__name__)


def register_all_middlewares(dispatcher: Dispatcher) -> None:      
    dispatcher.message.middleware.register(MailChatActionMiddleware(router=dispatcher))
    dispatcher.message.middleware.register(TTLCacheAlbumMiddleware(router=dispatcher))


# def set_scheduled_jobs(scheduler: AsyncIOScheduler, bot: Bot, *args, **kwargs) -> None:


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    storage = RedisStorage.from_url('redis://localhost:6379/0')
    jobstores = {
        'default': RedisJobStore(
            jobs_key='dispatched_trips_jobs',
            run_times_key='dispatched_trips_running',
            db=2
        )
    }
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores))
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(scheduler=scheduler, storage=storage)
    scheduler.ctx.add_instance(instance=bot, declared_class=Bot)

    register_all_middlewares(dispatcher=dispatcher)


    dispatcher.include_routers(
        commands.commands_router,
        mailing.router,
        pay_system.router,
        registration.router,
        subscription_system_calls.router,
        support.router,
        callbacks.router,
        email_list_action_calls.router,
        button_answers.router,
        audio_list_calls.router
        )
    
    setup_dishka(providers=[DatabaseProvider(), DALProvider(), ServiceProvider()], router=dispatcher)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot, skip_updates=True)
    finally:
        await dispatcher.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")