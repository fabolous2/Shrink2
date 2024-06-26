from typing import AsyncGenerator

from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession


from app.main.config import DATABASE_URL

from app.services import UserService, SettingsService, EmailService, AudioService, MailingService, ExtraMailing, AutoMailingManager
from app.data.dal import UserDAL, UserEmailDAL, UserAudioDAL, EmailSettingsDAL
from app.bot.utils import Encryption


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(url=DATABASE_URL)

    @provide(scope=Scope.APP, provides=async_sessionmaker[AsyncSession])
    def get_async_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def get_async_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
        async with sessionmaker() as session:
            yield session


class DALProvider(Provider):
    user_dal = provide(UserDAL, scope=Scope.REQUEST, provides=UserDAL)
    email_dal = provide(UserEmailDAL, scope=Scope.REQUEST, provides=UserEmailDAL)
    audio_dal = provide(UserAudioDAL, scope=Scope.REQUEST, provides=UserAudioDAL)
    settings_dal = provide(EmailSettingsDAL, scope=Scope.REQUEST, provides=EmailSettingsDAL)


class ServiceProvider(Provider):
    user_service = provide(UserService, scope=Scope.REQUEST, provides=UserService)
    settings_service = provide(SettingsService, scope=Scope.REQUEST, provides=SettingsService)
    email_service = provide(EmailService, scope=Scope.REQUEST, provides=EmailService)
    audio_service = provide(AudioService, scope=Scope.REQUEST, provides=AudioService)
    mailing_service = provide(MailingService, scope=Scope.REQUEST, provides=MailingService)
    encryption = provide(Encryption, scope=Scope.REQUEST, provides=Encryption)
    extra_mailing = provide(ExtraMailing, scope=Scope.REQUEST, provides=ExtraMailing)
    mailing_manager = provide(AutoMailingManager, scope=Scope.REQUEST, provides=AutoMailingManager)
