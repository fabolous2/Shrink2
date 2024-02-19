from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select, exists

from app.models import User
from app.data.models import User as UserDB


class UserDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def add(self, user: User) -> None:
        query = insert(UserDB).values(**asdict(user))
        await self.session.execute(query)
        await self.session.commit()

    async def update(self, user_id: int, **kwargs) -> None:
        query = update(UserDB).where(UserDB.user_id == user_id).values(**kwargs)

        await self.session.execute(query)
        await self.session.commit()

    async def exists(self, user_id: int) -> bool:
        query = select(exists().where(UserDB.user_id == user_id))

        result = await self.session.execute(query)

        return result.scalar_one()
    
    async def is_column_filled(self, user_id: int, *column_names: str) -> bool:
        # Проверка существования пользователя
        user_exists = await self.exists(user_id)
        
        if not user_exists:
            return False  # Пользователь не существует, колонка не заполнена

        query = select(getattr(UserDB, column_name) for column_name in column_names).where(UserDB.user_id == user_id)
        result = await self.session.execute(query)
        column_value = result.scalar_one_or_none()

        return column_value is not None
