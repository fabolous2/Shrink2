from app.models import EmailSettings
from app.data.dal import EmailSettingsDAL 


class SettingsService:
    def __init__(self, settings_dal: EmailSettingsDAL) -> None:
        self.settings_dal = settings_dal

    
    async def update_settings(self, user_id: int, **kwargs) -> None:
        await self.settings_dal.update(user_id, **kwargs)

        
    async def get_user_settings_content(self, user_id: int) -> EmailSettings:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings
    

    async def save_user_settings(self, settings: EmailSettings) -> None:
        exists = await self.settings_dal.exists(user_id=settings.user_id)

        if not exists:
            await self.settings_dal.add(settings)


    async def get_user_mail_subject(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)

        return settings.email_subject
    

    async def get_user_mail_text(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)

        return settings.email_text