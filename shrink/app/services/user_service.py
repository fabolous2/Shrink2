from app.models import User
from app.data.dal import UserDAL


class UserService:
    def __init__(self, user_dal: UserDAL) -> None:
        self.user_dal = user_dal
    
    async def save_user(self, user: User) -> None:
        exists = await self.user_dal.exists(user.user_id)

        if not exists:
            await self.user_dal.add(user)
    
    async def update_user(self, user_id: int, **kwargs) -> None:
        await self.user_dal.update(user_id, **kwargs)

    async def user_email_and_password_is_set(self, user_id: int) -> bool:
        """Заполнен ли email"""
        return await self.user_dal.is_column_filled(user_id, "personal_email", "password")
