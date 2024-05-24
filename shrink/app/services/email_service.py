from app.data.dal import UserEmailDAL

class EmailService:
    def __init__(
            self,
            email_dal: UserEmailDAL
    ) -> None:
        self.email_dal = email_dal


    async def update_email_list(self, emails: list) -> None:
        await self.email_dal.add(emails)
        
    async def get_count_matching_emails(self, user_id: int, email_list: list[str]):
        return await self.email_dal.count_matching_emails(user_id, email_list)


    async def get_user_email_list(self, user_id: int) -> str | None:
        emails = await self.email_dal.get_all(user_id=user_id, available_is = 1)
        if emails:
            email_addresses = [email.email_address for email in emails]
            return '\n'.join(email_addresses)
        return []
    
    
    async def get_unavailable_email_list(self, user_id: int) -> str | None:
        emails = await self.email_dal.get_all(user_id=user_id, available_is=0)
        if emails:
            email_addresses = [email.email_address for email in emails]
            final_list = '\n'.join(email_addresses)
            return final_list
        return []
        

    async def delete_emails_by_address(self, email_addresses: list[str]) -> None:
        for email_address in email_addresses:
            await self.email_dal.delete_address(email_address=email_address)
            
            
    async def delete_user_by_user_id(self, user_id: int) -> None:
        await self.email_dal.delete(user_id=user_id)
        
        

    async def update_index(self, emails: list[dict]) -> None:
        for email in emails:
            email.email_index += 1
        
        await self.email_dal.update(emails=emails)
        
        
    # async def update_available_is(self, emails: list[dict]) -> None:
    #     for email in emails:
    #         email.available_is = 1
        
    #     await self.email_dal.update(emails)
        
    async def update_available_is(self, user_id: int, email: str, available_is: int = 0) -> int:
        await self.email_dal.sub_ended(user_id, email, available_is=available_is)
        
        
    async def get_last_sent_email_by_user_id(self, user_id: int) -> str:
        return await self.email_dal.get_last_sent_email(user_id=user_id)
    
    
    async def available_email_list(self, user_id: int, available_is: int = 1) -> str:
        return await self.email_dal.get_available_email_list(user_id=user_id, 
                                                        available_is=available_is)
    
    async def get_last_sent_by_email(self, user_id: int, email: str) -> int:
        return await self.email_dal.get_last_sent_index_by_email(user_id, email)
        
        
    async def get_user_emails(self, user_id: int, available_is: int = 1):
        return await self.email_dal.get_user_emails(user_id=user_id, available_is=available_is)
    
    async def update_last_sent_index(self, user_id: int,  email_address: str, last_index: int):
        await self.email_dal.update_last_sent_index(user_id, email_address, last_index)
    
