from aiosmtplib import SMTPConnectError, SMTPSenderRefused
from typing import Annotated

from aiogram import Bot, Router, F
from aiogram.types import ContentType, Chat, User, Message
from aiogram.fsm.context import FSMContext
from aiogram_album import AlbumMessage

from app.bot.states import SelfMailingStatesGroup
from app.services import MailingService, EmailService, AudioService

from dishka.integrations.aiogram import inject, Depends


router = Router()

#Self - Mailing
@router.message(
        SelfMailingStatesGroup.WAIT_FOR_AUDIOS,
        F.media_group_id,
        flags={'chat_action': 'upload_document'}
)
@inject
async def self_mailing_handler(
    audio_messages: AlbumMessage,
    mailing_service: Annotated[MailingService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    user_data = await state.get_data()
    await state.clear()

    user_id = audio_messages.from_user.id
    emails_to = '\n'.join([email for email in user_data.values()]).split()

    await mailing_service.attach_message(user_id=user_id, emails_to=emails_to)

    for audio_msg in audio_messages:
        filename = audio_msg.audio.file_name

        audio_file_info = await bot.get_file(audio_msg.audio.file_id)
        audio_data = await bot.download_file(audio_file_info.file_path)
        await mailing_service.attach_audio(audio_data=audio_data, filename=filename)

    try:
        await mailing_service.connect(user_id=user_id)

    except SMTPConnectError:
        await bot.send_message(chat_id=event_chat.id, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")

    try:
        await mailing_service.send_email(user_id=user_id, emails_to=emails_to)
        await bot.send_message(chat_id=event_chat.id, text="Аудиофайл(ы) успешно отправлены на указанные адреса")

    except SMTPSenderRefused:
        await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")


@router.message(
        SelfMailingStatesGroup.WAIT_FOR_AUDIOS,
        F.content_type == ContentType.AUDIO,
        flags={'chat_action': 'upload_document'}
)
@inject
async def self_mailing_one_audio(
    audio_message: Message,
    mailing_service: Annotated[MailingService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    user_data = await state.get_data()
    await state.clear()

    user_id = audio_message.from_user.id
    emails_to = '\n'.join([email for email in user_data.values()]).split()
    await mailing_service.attach_message(user_id=user_id, emails_to=emails_to)

    filename = audio_message.audio.file_name
    audio_file_info = await bot.get_file(audio_message.audio.file_id)
    audio_data = await bot.download_file(audio_file_info.file_path)
    await mailing_service.attach_audio(audio_data=audio_data, filename=filename)

    try:
        await mailing_service.connect(user_id=user_id)
    except SMTPConnectError:
        await bot.send_message(chat_id=event_chat.id, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")

    try:
        await mailing_service.send_email(user_id=user_id, emails_to=emails_to)
        await bot.send_message(chat_id=event_chat.id, text="Аудиофайл(ы) успешно отправлены на указанные адреса")
    except SMTPSenderRefused:
        await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")


@router.message(SelfMailingStatesGroup.WAIT_FOR_AUDIOS, ~F.content_type == ContentType.AUDIO)
async def incorrect_file_format(
    bot: Bot,
    event_chat: Chat
) -> None:
    await bot.send_message(chat_id=event_chat.id, text="Вы отправили неверный формат файла. Оправлять можно только аудио")


#TODO: Auto-mailing
@inject
async def auto_mailing_handler(
    mailing_service: Annotated[MailingService, Depends()],
    email_service: Annotated[EmailService, Depends()],
    audio_service: Annotated[AudioService, Depends()],
    bot: Bot,
    event_chat: Chat,
    event_from_user: User         
) -> None:
    user_id = event_from_user.id
    emails_to = await email_service.get_user_email_list(user_id=user_id)
    audio_list = await audio_service.get_audio_list(user_id=user_id)

    await mailing_service.attach_message(user_id=user_id, emails_to=emails_to)

    for audio in audio_list:
        filename = audio[1]

        audio_file_info = await bot.get_file(audio[0])
        audio_data = await bot.download_file(audio_file_info.file_path)
        await mailing_service.attach_audio(audio_data=audio_data, filename=filename)

    try:
        await mailing_service.connect(user_id=user_id)

    except SMTPConnectError:
        await bot.send_message(chat_id=event_chat.id, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")

    try:
        await mailing_service.send_email(user_id=user_id, emails_to=emails_to)
        await bot.send_message(chat_id=event_chat.id, text="Аудиофайл(ы) успешно отправлены на указанные адреса")

    except SMTPSenderRefused:
        await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")
    

async def auto_mailing_verify() -> None:
    print("заработал")