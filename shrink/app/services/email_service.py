from dataclasses import astuple
from app.data.dal import UserEmailDAL


class EmailService:
    def __init__(self, email_dal: UserEmailDAL) -> None:
        self.email_dal = email_dal


    async def update_email_list(self, emails: list) -> None:
        await self.email_dal.add(emails)


    async def get_user_email_list(self, user_id: int) -> str:
        res = await self.email_dal.get_all(user_id=user_id)
        return '\n'.join(list(map(lambda x: astuple(x)[1], res))) 
    

    async def delete_emails(self, emails_to_del: list) -> None:
        return await self.email_dal.delete(emails_to_del=emails_to_del)
    