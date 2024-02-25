from dataclasses import astuple
from app.models import UserAudio
from app.data.dal import UserAudioDAL


class AudioService:
    def __init__(self, audio_dal: UserAudioDAL) -> None:
        self.audio_dal = audio_dal


    async def add_audio(self, audio_list: list) -> None:
        await self.audio_dal.add(audio_list)


    #TODO: get_audios
    # async def get_user_email_list(self, user_id: int) -> str:
    #     res = await self.email_dal.get_all(user_id=user_id)
    #     return '\n'.join(list(map(lambda x: astuple(x)[0], res))) 
    

    #TODO: Удаление 
    # async def delete_emails(self, emails_to_del: list) -> None:
    #     return await self.email_dal.delete(emails_to_del=emails_to_del)