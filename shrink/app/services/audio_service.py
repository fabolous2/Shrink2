from dataclasses import astuple
from app.data.dal import UserAudioDAL
from app.services import SettingsService


class AudioService:
    def __init__(
            self,
            audio_dal: UserAudioDAL,
            settings_service: SettingsService
    ) -> None:
        self.audio_dal = audio_dal
        self.settings_service = settings_service


    async def generate_index_service(self, user_id: int) -> tuple[int, int]:
        settings = await self.settings_service.get_user_settings_content(user_id=user_id)
        return await self.audio_dal.generate_index(user_id=user_id, amount=settings.amount)


    async def add_audio(self, audio_list: list | dict) -> None:
        await self.audio_dal.add(audio_list)


    async def get_audio_list(self, user_id: int) -> list:
        res = await self.audio_dal.get_all(user_id=user_id)
        return list(map(lambda x: astuple(x)[0], res))
    

    async def generate_album_indexes(self, user_id: int, audio_list: list[dict]) -> None:
        last_index, amount_left = await self.audio_dal.generate_index(user_id=user_id, amount=settings.amount)
        settings = await self.settings_service.get_user_settings_content(user_id=user_id)
        count = 0
        first_index = audio_list[0]["audio_index"]

        for i in range(len(audio_list)):
            temp = count // settings.amount + first_index
            audio_list[i]['audio_index'] = temp
            count += 1

    

    #TODO: Удаление 
    # async def delete_emails(self, emails_to_del: list) -> None:
    #     return await self.email_dal.delete(emails_to_del=emails_to_del)