from sqlalchemy import insert, select, exists, and_, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import UserAudio
from app.data.models import AudioFile, SentAudio, User, ArtistEmail

class UserAudioDAL:
    def __init__(
            self,
            session: AsyncSession
    ) -> None:
        self.session = session


    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(AudioFile, key) == value
              for key, value in kwargs.items()
              if hasattr(AudioFile, key))
        ))

        result = await self.session.execute(query)
        return result.scalar_one()


    async def add(self, user_audio: list | dict) -> None:
        query = insert(AudioFile).values(user_audio)
        await self.session.execute(query)
        await self.session.commit()


    async def get_one(self, **kwargs) -> UserAudio:
        query = select(AudioFile).filter_by(**kwargs)
        results = await self.session.execute(query)
        db_audio = results.scalar_one()

        return UserAudio(
            file_id=db_audio.audio_id,
            name=db_audio.audio_name,
            size=db_audio.size,
            user_id=db_audio.user_id,
            audio_index=db_audio.audio_index
        )


    async def get_all(self, **kwargs) -> list[UserAudio]:
        exists = await self.exists(**kwargs)
        
        if not exists:
            return None
        
        query = select(AudioFile).filter_by(**kwargs)

        results = await self.session.execute(query)
        db_audios = results.scalars().all()
     
        return [
            UserAudio(
                file_id=db_audio.audio_id,
                name=db_audio.audio_name,
                size=db_audio.size,
                user_id=db_audio.user_id,
                audio_index=db_audio.audio_index
            ) for db_audio in db_audios
        ]
    

    async def get_unsent_audio_ids(self) -> list[int]:
        query = (
            select(AudioFile.audio_id)
            .join(User, AudioFile.user_id == User.user_id)
            .join(ArtistEmail, User.user_id == ArtistEmail.user_id)
            .where(
                ~exists()
                .select()
                .where(
                    and_(
                        SentAudio.audio_id == AudioFile.audio_id,
                        SentAudio.email_id == ArtistEmail.email_id,
                    )
                )
            )
        )

        result = await self.session.execute(query)

        return [row for row in result.scalars()]


    async def get_last_index(self, user_id: int) -> int:
        query = (
            select(AudioFile.audio_index)
            .filter_by(user_id=user_id)
            .order_by(AudioFile.audio_index.desc())
        )
        results = await self.session.execute(query)
        last_index = results.scalars().first()

        return last_index


    async def generate_index(self, user_id: int, amount: int) -> tuple[int, int]:
        exists = await self.exists(user_id=user_id)
        
        if not exists:
            return 0, 0
        
        last_index = await self.get_last_index(user_id=user_id)
        query = select(func.count(AudioFile.audio_index)).where(
            and_(
                AudioFile.user_id == user_id,
                AudioFile.audio_index == last_index
            )
        )
        result = await self.session.execute(query)
        result = result.scalar_one()

        if result == amount:
            return last_index + 1, 0
        
        else:
            return  last_index, amount - result