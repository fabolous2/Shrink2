from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update, select, exists, delete, Result, and_

from app.models import User
from app.data.models import User as UserDB


class UserDAL:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def get_all_user_ids(self) -> list[int]:
        query = select(UserDB.user_id)  
        result = await self.session.execute(query) 
        user_ids = [row[0] for row in result.fetchall()]  
        return user_ids
    
    async def add(self, user: User) -> None:
        query = insert(UserDB).values(**asdict(user))
        await self.session.execute(query)
        await self.session.commit()

    async def update(self, user_id: int, **kwargs) -> None:
        query = update(UserDB).where(UserDB.user_id == user_id).values(**kwargs)

        await self.session.execute(query)
        await self.session.commit()

    async def exists(self, **kwargs) -> bool:
        query = select(
            exists().where(
                *(
                    getattr(UserDB, key) == value
                    for key, value in kwargs.items()
                    if hasattr(UserDB, key)
                )
            )
        )

        result = await self.session.execute(query)

        return result.scalar_one()

    async def is_column_filled(self, user_id: int, *column_names: str) -> bool:
        # Проверка существования пользователя
        user_exists = await self.exists(user_id=user_id)

        if not user_exists:
            return False  # Пользователь не существует, колонка не заполнена

        query = select(
            *(
                getattr(UserDB, column_name)
                for column_name in column_names
                if hasattr(UserDB, column_name)
            )
        ).where(UserDB.user_id == user_id)

        result = await self.session.execute(query)
        column_value = result.scalar_one_or_none()

        return column_value is not None

    async def _get(self, **kwargs) -> Result[tuple[UserDB]] | None:
        exists = await self.exists(**kwargs)

        if not exists:
            return None

        query = select(UserDB).filter_by(**kwargs)
        res = await self.session.execute(query)
        return res

    async def get_one(self, **kwargs) -> User | None:
        res = await self._get(**kwargs)

        if res:
            db_user = res.scalar_one_or_none()
            return User(
                user_id=db_user.user_id,
                personal_email=db_user.personal_email,
                password=db_user.password,
                secret=db_user.secret,
                subscription=db_user.subscription, 
                audio_limit=db_user.audio_limit, 
                email_limit=db_user.email_limit, 
                sub_duration=db_user.sub_duration
            )

    async def get_all(self, **kwargs) -> list[User] | None:
        res = await self._get(**kwargs)

        if res:
            db_users = res.scalars().all()
            return [
                User(
                    user_id=db_user.user_id,
                    personal_email=db_user.personal_email,
                    password=db_user.password,
                    secret=db_user.secret,
                    subscription=db_user.subscription, 
                    audio_limit=db_user.audio_limit,
                    sub_duration=db_user.sub_durations
                )
                for db_user in db_users
            ]
                 
    async def get_user_ids(self) -> list[int]:
        query = select(UserDB.user_id)  # Создаем запрос на выборку всех user_id
        result = await self.session.execute(query)  # Выполняем запрос
        user_ids = [row[0] for row in result.fetchall()] # Извлекаем user_id из результатов запроса
        return user_ids

    async def delete(self, **kwargs) -> None:
        # Построение списка условий для WHERE
        conditions = [
            getattr(UserDB, key) == value
            for key, value in kwargs.items()
            if hasattr(UserDB, key)
        ]
        
        # Собираем все условия с использованием and_()
        query = delete(UserDB).where(and_(*conditions))

        await self.session.execute(query)
        await self.session.commit()
