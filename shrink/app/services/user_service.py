from aiogram import Bot
from app.models import User
from app.data.dal import UserDAL, EmailSettingsDAL

from sqlalchemy import select
from app.models import User
from app.data.models import User as UserDB
from app.models.user import UserSubscription
from app.data.dal import UserEmailDAL, UserAudioDAL
from app.services.audio_service import AudioService
from app.services.email_service import EmailService


class UserService:
    def __init__(self, user_dal: UserDAL, settings_dal: EmailSettingsDAL,
                 audio_service: AudioService,
                email_service: EmailService,
                email_dal: UserEmailDAL,
                audio_dal: UserAudioDAL) -> None:
        self.user_dal = user_dal
        self.settings_dal = settings_dal
        self.audio_service = audio_service
        self.email_service = email_service
        self.email_dal = email_dal
        self.audio_dal = audio_dal

    async def exists(self, user_id):
        return await self.user_dal.exists(user_id=user_id)

    async def save_user(self, user: User) -> None:
        exists = await self.user_dal.exists(user_id=user.user_id)

        if not exists:
            await self.user_dal.add(user)
            
            
    async def get_all_user_ids(self):
        return await self.user_dal.get_all_user_ids()
    
    async def get_audio_limit(self, user_id: int):
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'audio_limit'):
            return user.audio_limit
        else:
            return False
        
    async def get_sub_duration(self, user_id: int):
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'sub_duration'):
            return user.sub_duration
        else:
            return None
  
    async def get_email_limit(self, user_id: int):
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'email_limit'):
            return user.email_limit
        else:
            return False
        
        
    async def update_user(self, user_id: int, **kwargs) -> None:
        await self.user_dal.update(user_id, **kwargs)
        
        
    
    async def user_is_registered(self, user_id: int) -> bool:
        return await self.user_dal.is_column_filled(user_id, "personal_email", "password")


    async def user_subscription(self, user_id: int) -> str:
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'subscription'):
            return user.subscription.value
        else:
            return False
        
        
    async def user_email_limit(self, user_id: int) -> str:
    
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'email_limit'):
            return user.email_limit.value
        else:
            return False    
        

    async def delete_user_by_user_id(self, user_id: int) -> None:
        await self.user_dal.delete(user_id=user_id)
        
        


    async def get_user_personal_email(self, user_id: int) -> str:
        user = await self.user_dal.get_one(user_id=user_id)
        if hasattr(user, 'personal_email'):
            return user.personal_email
        else:
            return False
        
        
    
    # async def get_user_ids(self) -> Union[List[int], bool]:
    #     # Получаем список всех пользователей из БД
    #     users = await self.user_dal.get_all()
        
    #     if users:
    #         user_ids = [user.user_id for user in users]
    #         return user_ids
    #     else:
    #         return []
        

    async def get_user_password(self, user_id: int) -> str:
        user = await self.user_dal.get_one(user_id=user_id)

        return user.password

    async def update_user_account(self, user_id: int, **kwargs) -> None:
        await self.user_dal.update(user_id, **kwargs)
        
    async def update_sub_duration(self, user_id: int, bot: Bot) -> None:
        sub = await self.user_dal.get_one(user_id = user_id)
        if sub.sub_duration > 0: 
            await self.user_dal.update(user_id, sub_duration=sub.sub_duration - 1)
        else:
            await bot.send_message(user_id, "Подписка закончилась!!!\nПочты, превышающие лимиты подписки 'free' будут недоступны")
            await self.user_dal.update(user_id, 
                                       email_limit=200, 
                                       audio_limit=20, 
                                       subscription=UserSubscription.NOT_SUBSCRIBED
                                       )
            await self.settings_dal.update(user_id, 
                                           email_limit_to_send=25)
            email_list = await self.email_dal.get_email_list(user_id)
            if len(email_list) > 200:
                email_list = email_list[-200:]
                print(email_list)
                for email in email_list:
                    await self.email_dal.sub_ended(user_id, email)
            
            audio_list = await self.audio_dal.get_audio_list_for_sub(user_id)
            if len(audio_list) > 20:
                final_audio_list = audio_list[-20:]
                print(final_audio_list)
                audio_dicts = [
                    {
                        'id': audio.id,
                        'file_id': audio.file_id,
                        'name': audio.name,
                        'size': audio.size,
                        'user_id': audio.user_id,
                        'audio_index': audio.audio_index,
                        'is_extra': audio.is_extra,
                        'available_is_for_audio': 0 
                    } for audio in final_audio_list
                ]
                await self.audio_dal.update(audio_dicts)
                
                
    async def update_email_limit_to_send_for_extra(self, user_id: int, bot: Bot) -> None:
        settings = await self.settings_dal.get_one(user_id = user_id)
        await self.settings_dal.update(user_id, email_limit_to_send_for_extra=50)