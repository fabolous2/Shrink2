from app.models import UserEmail
from app.data.dal import UserEmailDAL


class EmailService:
    def __init__(self, email_dal: UserEmailDAL) -> None:
        self.email_dal = email_dal


    async def update_email_list(self, user_emails: str, **kwargs) -> None:
        # эмайлы через пробел передаются?
        await self.email_dal.add(user_emails)

    async def get_user_email_list(self, user_id: int) -> UserEmail:
        return await self.email_dal.get_all(user_id)

#пользователь должен отправить почты либо каждую с новой строки либо через зяпятуючЧ
