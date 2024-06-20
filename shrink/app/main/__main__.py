import datetime
import logging
import asyncio
from typing import Annotated
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.jobstores.redis import RedisJobStore
from dishka.integrations.aiogram import setup_dishka, make_async_container
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.main.config import BOT_TOKEN
from app.main.ioc import DatabaseProvider, DALProvider, ServiceProvider
from app.bot.handlers import commands, button_answers, pay_master, registration, mailing, admin
from app.bot.callbacks import support, callbacks, subscription_system_calls, audio_list_calls
from app.bot.middlewares.album_middleware import TTLCacheAlbumMiddleware
from app.bot.middlewares.chat_actions_middleware import MailChatActionMiddleware
from apscheduler_di import ContextSchedulerDecorator


from app.bot.callbacks import email_list_action_calls


logger = logging.getLogger(__name__)


def register_all_middlewares(dispatcher: Dispatcher) -> None:      
    dispatcher.message.middleware.register(MailChatActionMiddleware(router=dispatcher))
    dispatcher.message.middleware.register(TTLCacheAlbumMiddleware(router=dispatcher))
   
   
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
            db=2,
            host='localhost',
            db=2,
            port=6379
        )
    }
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone="Europe/Moscow", jobstores=jobstores))
# "6435829256:AAFEouFajhSIHyX08x3xaZWv2bSbnujBZTI"
    bot = Bot(token="6435829256:AAFEouFajhSIHyX08x3xaZWv2bSbnujBZTI", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(scheduler=scheduler, storage=storage) 
    scheduler.ctx.add_instance(instance=bot, declared_class=Bot)

    dispatcher.message.middleware.register(MailChatActionMiddleware(router=dispatcher))
    TTLCacheAlbumMiddleware(router=dispatcher, latency=0.5)

    dispatcher.include_routers(
        admin.admin,
        button_answers.router,
        commands.commands_router,
        mailing.router,
        registration.router,
        callbacks.router,
        email_list_action_calls.router,
        audio_list_calls.router,
        pay_master.router,
        subscription_system_calls.router,
        support.router
        )   
    print(make_async_container(DatabaseProvider(), DALProvider(), ServiceProvider()))
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