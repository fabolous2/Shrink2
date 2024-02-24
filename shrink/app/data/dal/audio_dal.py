from dataclasses import asdict

from sqlalchemy import insert,select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserAudio
from app.data.models import UserAudio as UserAudioDB

class UserAudioDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_audio: UserAudio) -> None:
        query = insert(UserAudioDB).values(**asdict(user_audio))
        
        await self.session.execute(query)
        await self.session.commit()

    async def get_one(self, **kwargs) -> UserAudio:
        query = select(UserAudioDB).filter_by(**kwargs)

        results = await self.session.execute(query)

        db_audio = results.scalar_one()

        return UserAudio(
            file_id=db_audio.file_id,
            name=db_audio.name,
            size=db_audio.size,
            is_sent=db_audio.is_sent,
            user_id=db_audio.user_id
        )

    async def get_all(self, **kwargs) -> list[UserAudio]:
        query = select(UserAudioDB).filter_by(**kwargs)

        results = await self.session.execute(query)

        db_audios = results.scalars().all()

        return [
            UserAudio(
                file_id=db_audio.file_id,
                name=db_audio.name,
                size=db_audio.size,
                is_sent=db_audio.is_sent,
                user_id=db_audio.user_id
            ) for db_audio in db_audios
        ]
