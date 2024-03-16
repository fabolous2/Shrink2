from aiogram import Bot
from aiogram.types import Chat
from aiogram_album import AlbumMessage

from aiosmtplib import SMTP, SMTPConnectError, SMTPSenderRefused, SMTPAuthenticationError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

from app.services import UserService, SettingsService, AudioService, EmailService
from app.bot.utils.errors import (
    SchedulerNotSetError,
    AudioNotAddedError,
    EmailAudioNotAddedError,
    EmailNotAddedError,
    NotAvailableToSend)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.data.dal import UserEmailDAL, UserAudioDAL
from app.models import UserAudio


class MailingService:
    def __init__(
            self,
            settings_service: SettingsService,
            user_service: UserService,
            audio_service: AudioService,
            email_service: EmailService,
            email_dal: UserEmailDAL,
            audio_dal: UserAudioDAL
    ) -> None:
        self.settings_service = settings_service
        self.user_service = user_service
        self.email_message = MIMEMultipart()
        self.client = SMTP(hostname='smtp.gmail.com', port=587)
        self.scheduler = AsyncIOScheduler()
        self.audio_service = audio_service
        self.email_service = email_service
        self.email_dal = email_dal
        self.audio_dal = audio_dal

    async def connect(self, user_id: int) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        password = await self.user_service.get_user_password(user_id=user_id)
        await self.client.connect(
            start_tls=True, validate_certs=False, username=user_email, password=password
        )


    async def attach_audio(self, audio: AlbumMessage | UserAudio, bot: Bot) -> None:
        filename = audio.name if type(audio) == UserAudio else audio.audio.file_name
        audio_file_info = await bot.get_file(
            audio.file_id 
            if type(audio) == UserAudio
            else audio.audio.file_id
        )
        audio_data = await bot.download_file(audio_file_info.file_path)

        file = MIMEBase('audio', 'mp3')
        file.set_payload(audio_data.read())
        encoders.encode_base64(file)
        file.add_header('content-disposition','attachment', filename=filename)
        self.email_message.attach(file)
    
    
    async def attach_message(
            self,
            user_id: int,
            emails_to: list
    ) -> None:
        message = await self.settings_service.get_user_mail_text(user_id=user_id)

        self.email_message['From'] = await self.user_service.get_user_personal_email(user_id=user_id)
        self.email_message['Subject'] = await self.settings_service.get_user_mail_subject(user_id=user_id)
        self.email_message['To'] = emails_to
        self.email_message.attach(MIMEText(f"<html><body>{message}</body></html>", "html", "utf-8"))

    
    async def send_email(self, user_id: int, emails_to: str) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        async with self.client as client:
            await client.sendmail(
                user_email,
                emails_to,
                self.email_message.as_string()
            )
            await client.quit()


    async def auto_send_email(self, user_id: int, emails_to: str, index: int) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        async with self.client as client:
            await client.sendmail(
                user_email,
                emails_to,
                self.email_message.as_string()
            )
            await self.email_dal.update_index(user_id=user_id, index=index)
            await client.quit()        
        

    async def auto_mailing_starter(self, user_id: int, bot: Bot, event_chat: Chat) -> None:
        email_indexes = await self.email_dal.count_emails_to_send(user_id=user_id)
        email_amount = len(email_indexes) if len(email_indexes)>0 else None
        print(email_indexes)
        if not email_amount:
            raise NotAvailableToSend("User must add more email addresses or audio files")

        for email_index in email_indexes:
            print(email_index)
            audio_list = await self.audio_dal.get_auto_mailing_audio(user_id=user_id, email_indexes=email_index)
            email_list = await self.email_dal.get_auto_email_list(user_id=user_id, indexes=email_index)
            emails_to = ', '.join(email_list)
            print(emails_to)
            print(audio_list)
            await self.attach_message(user_id=user_id, emails_to=emails_to)
            [await self.attach_audio(audio=audio, bot=bot) for audio in audio_list]

            try:
                await self.connect(user_id=user_id)
                await self.auto_send_email(user_id=user_id, emails_to=emails_to, index=email_index)
                
            except SMTPConnectError:
                await bot.send_message(chat_id=event_chat, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")     
            except SMTPSenderRefused:
                await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")

        await bot.send_message(chat_id=event_chat.id, text="Успешно разосланы письма! Следующая рассылка в - (время)")


    async def turn_on_mailing(self, user_id: int, bot: Bot, event_chat: Chat) -> None:
        schedule_time = await self.settings_service.get_user_scheduler(user_id=user_id)
        audios =  await self.audio_service.get_audio_list(user_id=user_id)
        emails = await self.email_service.get_user_email_list(user_id=user_id)

        if schedule_time:
            try:
                self.scheduler.remove_all_jobs()
                self.scheduler.add_job(
                    func=self.auto_mailing_starter,
                    trigger="interval",
                    seconds=10,
                    kwargs={'user_id': user_id, 'bot': bot, 'event_chat': event_chat}
                )
                self.scheduler.start()
                await self.settings_service.update_settings(user_id=user_id, is_turned_on=True)

            except NotAvailableToSend:
                await bot.send_message(
                    chat_id=event_chat.id,
                    text='Список доступных почт для отправки закончился. Пополните список почт, либо список аудио'
                )
            except SMTPAuthenticationError:
                await bot.send_message(
                    chat_id=event_chat.id,
                    text='Не удалось ауденцифитироваться в ва'
                )
        elif not schedule_time:
            raise SchedulerNotSetError("Scheduler is not set")
        elif not audios and not emails:
            raise EmailAudioNotAddedError("user haven't got any audios and emails in database")
        elif not audios:
            raise AudioNotAddedError("user haven't got any audios in database")
        elif not emails:
            raise EmailNotAddedError("user haven't got any emails in database")


    async def turn_off_scheduler(self, user_id: int) -> None:
        self.scheduler.remove_all_jobs()
        await self.settings_service.update_settings(user_id=user_id, is_turned_on=False) 
    

    async def test(self, user_id: int) -> None:
        await self.email_dal.count_emails_to_send(user_id=user_id)