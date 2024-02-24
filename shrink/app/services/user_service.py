from app.models import User
from app.data.dal import UserDAL, EmailSettingsDAL


class UserService:
    def __init__(self, user_dal: UserDAL, settings_dal: EmailSettingsDAL) -> None:
        self.user_dal = user_dal
        self.settings_dal = settings_dal
    

    async def save_user(self, user: User) -> None:
        exists = await self.user_dal.exists(user_id=user.user_id)

        if not exists:
            await self.user_dal.add(user)


    async def update_user(self, user_id: int, **kwargs) -> None:
        await self.user_dal.update(user_id, **kwargs)


    async def user_email_and_password_is_set(self, user_id: int) -> bool:
        """Заполнен ли email"""
        return await self.user_dal.is_column_filled(user_id, "personal_email", "password")


    async def user_subscription(self, user_id: int) -> str:
        user = await self.user_dal.get_one(user_id=user_id)

        return user.subscription.value


    async def delete_user_by_user_id(self, user_id: int) -> None:
        await self.user_dal.delete(user_id=user_id)


    async def get_user_personal_email(self, user_id: int) -> str:
        user = await self.user_dal.get_one(user_id=user_id)

        return user.personal_email
    

    async def update_user_account(self, user_id: int, **kwargs) -> None:
        user = await self.user_dal.update(user_id, **kwargs)

