from app.models import EmailSettings
from app.data.dal import EmailSettingsDAL , UserAudioDAL, UserEmailDAL
from app.data.models import Base


class SettingsService:
    def __init__(
            self,
            settings_dal: EmailSettingsDAL,
            audio_dal: UserAudioDAL,
            email_dal: UserEmailDAL
    ) -> None:
        self.settings_dal = settings_dal
        self.audio_dal = audio_dal
        self.email_dal = email_dal

    
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
    

    async def get_user_scheduler(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.schedule_time
    
    
    async def get_amount(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.amount


    async def set_amount(self, user_id: int, amount: int) -> None:
        audio_list = await self.audio_dal.get_all(user_id=user_id)
        email_list = await self.email_dal.get_all(user_id=user_id)
        old_amount = await self.get_amount(user_id=user_id)
        if not audio_list:
            await self.settings_dal.update(user_id, amount=amount)

        audio_list = [
            {
            'id': audio.id,
            'audio_id': audio.file_id,
            'user_id': audio.user_id,
            'audio_index': 0
            }
            for audio in audio_list
        ]
        email_list = [
            {
            'id': email.id,
            'email_address': email.email_address,
            'user_id': email.user_id,
            'email_id': email.email_id*old_amount//int(amount),
            }
            for email in email_list
        ]

        count = 0
        for i in range(len(audio_list)):
            temp = count // int(amount)
            audio_list[i]['audio_index'] = temp
            count += 1

        await self.settings_dal.update(user_id=user_id, amount=amount)
        await self.email_dal.update(email_list=email_list)
        await self.audio_dal.update(audio_list=audio_list)
