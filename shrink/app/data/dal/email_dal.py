from sqlalchemy import insert, select, exists, delete, update, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserEmail
from app.data.models import ArtistEmail as UserEmailDB, AudioFile


class UserEmailDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    

    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(UserEmailDB, key) == value
              for key, value in kwargs.items()
              if hasattr(UserEmailDB, key))
        ))
        result = await self.session.execute(query)
        return result.scalar_one()


    async def add(self, user_emails: list) -> None:
        query = insert(UserEmailDB).values(user_emails)
        await self.session.execute(query)
        await self.session.commit()


    async def get_one(self, **kwargs) -> UserEmail:
        exists = await self.exists(**kwargs)
        if not exists:
            return None
        
        query = select(UserEmailDB).filter_by(**kwargs)
        results = await self.session.execute(query)
        db_email = results.scalar_one()

        return UserEmail(
            id=db_email.id,
            email_id=db_email.email_id,
            email_address=db_email.email_address, 
            user_id=db_email.user_id
        )


    async def get_all(self, **kwargs) -> list[UserEmail]:
        exists = await self.exists(**kwargs)
        if not exists:
            return None
        
        query = select(UserEmailDB).filter_by(**kwargs)
        results = await self.session.execute(query)
        db_emails = results.scalars().all()

        return [
            UserEmail(
                id=db_email.id,
                email_id=db_email.email_id,
                email_address=db_email.email_address, 
                user_id=db_email.user_id
            ) for db_email in db_emails
        ]


    async def delete(self, **kwargs) -> None:
        query = delete(UserEmailDB).where(
            {
                getattr(UserEmailDB, key) == value
                for key, value in kwargs.items()
                if hasattr(UserEmailDB, key)
            }
        )
        await self.session.execute(query)
        await self.session.commit()

    
    async def update(self, email_list: list[dict]) -> None:
        query = update(UserEmailDB)
        await self.session.execute(query, email_list)
        await self.session.commit()

    
    async def update_index(self, user_id: int, index: list) -> None:
        query = (
            update(UserEmailDB)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_id.in_(index)
                )
            )
            .values(email_id=UserEmailDB.email_id + 1)
        )
        await self.session.execute(query)
        await self.session.commit()

    
    async def get_email_indexes_to_send(self, user_id: int) -> int | None:
        subquery = (
            select(func.max(AudioFile.audio_index))
            .filter_by(user_id=user_id)
            .group_by(AudioFile.audio_index)
        )

        query = (select(
                func.max(UserEmailDB.email_id)
        )
        .where(
            and_(
                UserEmailDB.user_id == user_id,
                UserEmailDB.email_id.in_(subquery)
            )
        )
        .group_by(UserEmailDB.email_id) 
        )
        result = await self.session.execute(query)
        result = result.scalars().all()

        return result
    

    async def get_auto_email_list(self, user_id: int, indexes: int) -> list:
        query = (
            select(UserEmailDB.email_address)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_id == indexes
                )
            )
        )
        email_list = await self.session.execute(query)
        email_list = email_list.scalars().all()
        return email_list