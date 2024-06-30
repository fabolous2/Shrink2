from app.models import EmailSettings
from app.data.dal import EmailSettingsDAL , UserAudioDAL, UserEmailDAL

from apscheduler.schedulers.asyncio import AsyncIOScheduler


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
        self.scheduler = AsyncIOScheduler()

    async def get_settings(self, **kwargs) -> EmailSettings:
        return await self.settings_dal.get_one(**kwargs)
    
    async def update_settings(self, user_id: int, **kwargs) -> None:
        await self.settings_dal.update(user_id, **kwargs)
    
    async def get_user_settings_content(self, user_id: int) -> EmailSettings:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings if settings else None
    
    async def delete_user_by_user_id(self, user_id: int) -> None:
        await self.settings_dal.delete(user_id=user_id)
    
    async def save_user_settings(self, settings: EmailSettings) -> None:
        exists = await self.settings_dal.exists(user_id=settings.user_id)
        if not exists:
            await self.settings_dal.add(settings)

    async def get_user_mail_subject(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        if settings:    
            return settings.email_subject
        return "None"
    
    async def get_frequency(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        if settings.frequency:
            return settings.frequency
        return "None"
    
    async def get_email_limit_to_send(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        if settings.email_limit_to_send:
            return settings.email_limit_to_send
        return "None"
    
    async def get_current_frequency(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        if settings:
            return settings.current_frequency
        return "None"
    
    async def get_user_mail_text(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        if settings:    
            return settings.email_text
        return "None"
        
    async def get_user_scheduler(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.schedule_time
    
    async def get_amount(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.amount
    
    async def get_email_limit_to_send_for_extra(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.email_limit_to_send_for_extra
    
    async def get_advice_for_frequency(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.advice_for_frequency
    
    async def get_advice_for_quantity(self, user_id: int) -> str:
        settings = await self.settings_dal.get_one(user_id=user_id)
        return settings.advice_for_quantity

    
    async def update_last_update_frequency_by_time(self, user_id: int):
        self.scheduler.add_job(self.update_last_update_frequency,
                               trigger="cron",
                               hour=17,
                               minute=18,
                               kwargs={'user_id': user_id})
        self.scheduler.start()
        
    async def update_last_update_frequency(self, user_id: int):
        await self.settings_dal.update(user_id=user_id, current_frequency=1)        
        
    async def update_email_limit_to_send(self, user_id: int, count: int):
        await self.settings_dal.update(user_id=user_id, email_limit_to_send=count)

    async def set_amount(self, user_id: int, amount: int) -> None:
        audio_list = await self.audio_dal.get_all(user_id=user_id, available_is_for_audio=1, is_extra=0)
        email_list = await self.email_dal.get_all(user_id=user_id, available_is=1)
        old_amount = await self.get_amount(user_id=user_id)
        
        
        if not audio_list:
            audio_list = []
            await self.settings_dal.update(user_id, amount=amount)
            
        email_list = [] if not email_list else email_list
            
        if not old_amount:
            old_amount = 1
            
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
    
