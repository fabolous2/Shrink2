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
            user_id=db_email.user_id, 
            available_is=db_email.available_is
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
                user_id=db_email.user_id, 
                available_is=db_email.available_is
            ) for db_email in db_emails
        ]


    async def delete(self, **kwargs) -> None:
        query = delete(UserEmailDB).where(
        and_(
            *(getattr(UserEmailDB, key) == value
              for key, value in kwargs.items()
              if hasattr(UserEmailDB, key))
            )
        )
        await self.session.execute(query)
        await self.session.commit()
        
        
    async def delete_address(self, email_address: str) -> None:
        query = delete(UserEmailDB).where(UserEmailDB.email_address == email_address)
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
        
        
    async def increment_indexes(self, user_id: int, emails: list[str]) -> None:
        query = (
            update(UserEmailDB)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_address.in_(emails)
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
    
    async def get_email_list(self, user_id: int) -> list:
        query = (
            select(UserEmailDB.email_address)
            .where(
                and_(
                    UserEmailDB.user_id == user_id
                )
            )
        )
        email_list = await self.session.execute(query)
        email_list = email_list.scalars().all()
        return email_list
    
    
    async def get_email_id(self, user_id: int, email: str) -> int:
        query = (
            select(UserEmailDB.email_id)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_address == email
                )
            )
        )
        id = await self.session.execute(query)
        id = id.scalar()
        return id
        
    
    async def get_last_sent_email(self, user_id: int) -> str:
        query = (
            select(UserEmailDB.email_address)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.last_sent_index == 1
                )
            )
        )
        email = await self.session.execute(query)
        email = email.scalar()
        return email
    
    
    async def get_user_emails(self, user_id: int, available_is: int = 1) -> list[str]:
        query = (
            select(UserEmailDB.email_address)
            .where(UserEmailDB.user_id == user_id, 
                   UserEmailDB.available_is == available_is)
        )
        result = await self.session.execute(query)
        email_addresses = [row for row in result.scalars()]
        return email_addresses
    
    
    async def count_matching_emails(self, user_id: int, email_list: list[str]) -> int:
        query = (
            select(func.count())
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_address.in_(email_list)
                )
            )
        )
        result = await self.session.execute(query)
        matching_count = result.scalar()
        return matching_count
    
    
    async def update_last_sent_index(self, user_id: int,  email_address: str, last_index) -> None:
        query = (
            update(UserEmailDB)
            .where(UserEmailDB.user_id == user_id,
                   UserEmailDB.email_address == email_address
                   )
            .values(last_sent_index=last_index)
        )
        await self.session.execute(query)
        await self.session.commit()
        
        
        
        
    async def sub_ended(self, user_id: int,  email_address: str, available_is: int = 0) -> None:
        query = (
            update(UserEmailDB)
            .where(UserEmailDB.user_id == user_id,
                   UserEmailDB.email_address == email_address
                   )
            .values(available_is=available_is)
        )
        await self.session.execute(query)
        await self.session.commit()
        
        
    async def get_last_sent_index_by_email(self, user_id: int, email: str) -> int:
        query = (
            select(UserEmailDB.last_sent_index)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.email_address == email
                )
            )
        )
        index = await self.session.execute(query)
        index = index.scalar()
        return index
    
    async def get_available_email_list(self, user_id: int, available_is: int = 1) -> list:
        query = (
            select(UserEmailDB.email_address)
            .where(
                and_(
                    UserEmailDB.user_id == user_id,
                    UserEmailDB.available_is == available_is
                )
            )
        )
        email_list = await self.session.execute(query)
        email_list = email_list.scalars().all()
        return email_list
    