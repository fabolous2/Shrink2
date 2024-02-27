from typing import Annotated

from aiogram import Bot, Router, F
from aiogram.types import ContentType, Chat
from aiogram.fsm.context import FSMContext
from aiogram_album import AlbumMessage

from app.bot.states import SelfMailingStatesGroup
from app.services import MailingService, UserService, SettingsService

from dishka.integrations.aiogram import inject, Depends


router = Router()


#Self - Mailing
@router.message(SelfMailingStatesGroup.WAIT_FOR_AUDIOS, F.media_group_id)
@inject
async def self_mailing_handler(
    audio_messages: AlbumMessage,
    mailing_service: MailingService,
    user_service: Annotated[UserService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    user_data = await state.get_data()
    user_id = audio_messages.from_user.id
    await state.clear()
    print(user_id)
    email_from = await user_service.get_user_personal_email(user_id=user_id)
    user_password = await user_service.get_user_password(user_id=user_id)
    email_message = await settings_service.get_user_mail_text(user_id=user_id)
    emails_to = '\n'.join([email for email in user_data.values()]).split()
    
    audio_info = await mailing_service.conduct_audio_info(audio_messages=audio_messages)
    print(audio_info)
    [
        await mailing_service.attach_audio(audio=audio, bot=bot, email_message=email_message)
        for audio in audio_info
    ]
    
    try:
        await mailing_service.login(user_email=email_from, password=user_password)
        await mailing_service.sending_email(email_from=email_from, emails_to=emails_to, email_message=email_message)
        await bot.send_message(chat_id=event_chat.id, text="Аудиофайл(ы) успешно отправлены на указанные адреса")
    
    except Exception:
        await bot.send_message(chat_id=event_chat.id, text=...)


#TODO: Auto-Mailing
# async def auto_mailing_handler()