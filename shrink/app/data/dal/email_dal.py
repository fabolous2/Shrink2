from dataclasses import asdict

from sqlalchemy import insert, select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserEmail
from app.data.models import UserEmail as UserEmailDB


class UserEmailDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    

    async def exists(self, **kwargs) -> bool:
        query = select(exists().where(
            *(getattr(UserEmailDB, key) == value for key, value in kwargs.items() if hasattr(UserEmailDB, key))
        ))

        # делаю так чтобы проверять на существование не только по id
        
        result = await self.session.execute(query)

        return result.scalar_one()


    async def add(self, user_email: UserEmail) -> None:
        query = insert(UserEmailDB).values(**asdict(user_email))
        
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
            to=db_email.to, 
            user_id=db_email.user_id,
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
                to=db_email.to, 
                user_id=db_email.user_id,
            ) for db_email in db_emails
        ]
