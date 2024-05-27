from app.data.dal import UserAudioDAL
from app.services.settings_service import SettingsService

from aiogram_album import AlbumMessage


class AudioService:
    def __init__(
            self,
            audio_dal: UserAudioDAL,
            settings_service: SettingsService
    ) -> None:
        self.audio_dal = audio_dal
        self.settings_service = settings_service
        
        
    async def delete_user_by_user_id(self, user_id: int) -> None:
        await self.audio_dal.delete(user_id=user_id)
        
    async def delete_audio(self, user_id: int, filename: str, size: int) -> None:
        await self.audio_dal.delete_audio_by_criteria(user_id, filename, size)
        
    async def delete_extra_audio(self, user_id: int) -> None:
        await self.audio_dal.delete_extra_audios(user_id)


    async def generate_index_service(self, user_id: int) -> tuple[int, int]:
        settings = await self.settings_service.get_user_settings_content(user_id=user_id)
        return await self.audio_dal.generate_index(user_id=user_id, amount=settings.amount)


    async def add_audio(self, audio_list: list | dict) -> None:
        await self.audio_dal.add(audio_list)


    async def get_audio_list(self, user_id: int, is_extra: int = 0, available_is: int = 1) -> list | None:
        audio = await self.audio_dal.get_all(user_id=user_id, is_extra = is_extra, 
                                             available_is_for_audio = available_is)
        if audio:
            return audio
        return []
    

    async def generate_album_indexes(self, user_id: int, audio_list: list[dict]) -> None:
        last_index, amount_left = await self.audio_dal.generate_index(user_id=user_id, amount=settings.amount)
        settings = await self.settings_service.get_user_settings_content(user_id=user_id)
        count = 0
        first_index = audio_list[0]["audio_index"]

        for i in range(len(audio_list)):
            temp = count // settings.amount + first_index
            audio_list[i]['audio_index'] = temp
            count += 1
    

    async def create_audio_list(self, user_id: int, album_message: AlbumMessage, is_extra: int = 0) -> list[dict]:
        index, amount_left = await self.generate_index_service(user_id=user_id)
        settings = await self.settings_service.get_user_settings_content(user_id=user_id)
        audio_list = [
            {
            'audio_id': audio_message.audio.file_id,
            'audio_name': audio_message.audio.file_name,
            'size': audio_message.audio.file_size,
            'user_id': audio_message.from_user.id,
            'audio_index': index, 
            'is_extra': is_extra, 
            'available_is_for_audio': 1
            }
            for audio_message in album_message if audio_message.audio and audio_message.audio.mime_type == 'audio/mpeg'
        ]
        start_index = 0
        count = 0

        if amount_left != 0:
            for audio in audio_list[:amount_left]:
                start_index += 1
                count += 1
            
        first_index = audio_list[start_index - 1]["audio_index"]
        if not settings.amount:
           settings.amount = 2
        for i in range(len(audio_list)):
            temp = count // settings.amount + first_index
            audio_list[i]['audio_index'] = temp
            count += 1

        return audio_list
    
    
    async def create_audio_list_extra(self, user_id: int, album_message: AlbumMessage, is_extra: int = 0) -> list[dict]:
        audio_list = [
            {
            'audio_id': audio_message.audio.file_id,
            'audio_name': audio_message.audio.file_name,
            'size': audio_message.audio.file_size,
            'user_id': audio_message.from_user.id,
            'audio_index': 0, 
            'is_extra': is_extra
            }
            for audio_message in album_message if audio_message.audio
        ]
        return audio_list
    
    async def delete_audio_list(self, user_id: int, audio_list: list[dict]) -> None:
        try:
            for audio in audio_list:
                await self.audio_dal.delete_audio_by_criteria(user_id, audio.get('audio_name'), audio.get('size'))
        except Exception as ex:
            print(f"Ошибка при удалении аудиофайлов: {ex}")
            
            
    async def update_audio_list(self, user_id: int, **kwargs) -> None:
        await self.audio_dal.update(user_id, **kwargs)
    
    