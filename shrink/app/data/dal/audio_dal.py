from dataclasses import asdict

from sqlalchemy import insert, select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserAudio
from app.data.models import UserAudio as UserAudioDB

class UserAudioDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(UserAudioDB, key) == value
              for key, value in kwargs.items()
              if hasattr(UserAudioDB, key))
        ))

        result = await self.session.execute(query)
        return result.scalar_one()


    async def add(self, user_audio: list | dict) -> None:
        query = insert(UserAudioDB).values(user_audio)
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
        exists = await self.exists(**kwargs)
        
        if not exists:
            return None
        
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
