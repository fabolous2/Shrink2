from sqlalchemy import insert, select, exists, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserEmail
from app.data.models import ArtistEmail as UserEmailDB


class UserEmailDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    

    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(UserEmailDB, key) == value for key, value in kwargs.items() if hasattr(UserEmailDB, key))
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