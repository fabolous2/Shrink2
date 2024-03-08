from dataclasses import astuple
from app.data.dal import UserAudioDAL


class AudioService:
    def __init__(self, audio_dal: UserAudioDAL) -> None:
        self.audio_dal = audio_dal


    async def add_audio(self, audio_list: list | dict) -> None:
        await self.audio_dal.add(audio_list)


    async def get_audio_list(self, user_id: int) -> list:
        res = await self.audio_dal.get_all(user_id=user_id)
        return list(map(lambda x: astuple(x)[0], res))
    

    #TODO: Удаление 
    # async def delete_emails(self, emails_to_del: list) -> None:
    #     return await self.email_dal.delete(emails_to_del=emails_to_del)