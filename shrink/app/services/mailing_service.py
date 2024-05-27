import datetime
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
    EmailNotAddedError)

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


    async def send_email(self, user_id: int, emails_to: list) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        self.email_message['From'] = user_email

        async with self.client as client:
            await client.sendmail(
                user_email,
                emails_to,
                self.email_message.as_string()
            )
            await client.quit()


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
            user_id: int
        ) -> None:
        message = await self.settings_service.get_user_mail_text(user_id=user_id)
        subject = await self.settings_service.get_user_mail_subject(user_id=user_id)
        print(message, subject)
        
        if message is not None and subject is not None:
            email_text = f"<html><body>{message}</body></html>"
            self.email_message.attach(MIMEText(email_text, "html", "utf-8"))
            self.email_message['Subject'] = subject
        elif message is not None:
            email_text = f"<html><body>{message}</body></html>"
            self.email_message.attach(MIMEText(email_text, "html", "utf-8"))
        elif subject is not None:
            self.email_message.attach(MIMEText("", "plain", "utf-8"))
            self.email_message['Subject'] = subject
        else:
            self.email_message.attach(MIMEText("", "plain", "utf-8"))
            
    async def attach_message_for_extra(
            self, subject, desc
        ) -> None:
        if desc is not None and subject is not None:
            email_text = f"<html><body>{desc}</body></html>"
            self.email_message.attach(MIMEText(email_text, "html", "utf-8"))
            self.email_message['Subject'] = subject
        elif desc is not None:
            email_text = f"<html><body>{desc}</body></html>"
            self.email_message.attach(MIMEText(email_text, "html", "utf-8"))
        elif subject is not None:
            self.email_message.attach(MIMEText("", "plain", "utf-8"))
            self.email_message['Subject'] = subject
        else:
            self.email_message.attach(MIMEText("", "plain", "utf-8"))


    async def auto_send_email(self, user_id: int, emails_to: list) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        self.email_message['From'] = user_email

        async with self.client as client:
            await client.sendmail(
                user_email,
                emails_to,
                self.email_message.as_string()
            )
            self.email_message = MIMEMultipart()
            await client.quit()


    async def auto_mailing(self, user_id: int, bot: Bot, event_chat: Chat, email_indexes: list[int]) -> None:
        print(email_indexes)
        
        final_list_to_send = []
        tmp_list = []
        need_to_del = True
        COUNT = await self.settings_service.get_email_limit_to_send(user_id=user_id)

        list_to_send = await self.email_dal.get_user_emails(user_id=user_id)
        print(list_to_send)
        last_sent_email = (await self.email_dal.get_last_sent_email(user_id=user_id)) 
        
        if not last_sent_email in list_to_send:
            last_sent_email = list_to_send[0] 
            
        last_index = list_to_send.index(last_sent_email)
        
        tmp_last_sent_email_index = await self.email_dal.get_email_id(user_id=user_id, 
                                                         email=last_sent_email)
        
        
        if not tmp_last_sent_email_index in email_indexes:
            list_to_check = list_to_send[last_index:] + list_to_send[0:last_index+1]
            print("list to check", list_to_check)
            for email in list_to_check:
                email_id = await self.email_dal.get_email_id(user_id=user_id, 
                                                            email=email)
                if email_id in email_indexes:
                    await self.email_dal.update_last_sent_index(user_id=user_id, 
                                                    email_address=last_sent_email, 
                                                    last_index = 0)
                    await self.email_dal.update_last_sent_index(user_id=user_id, 
                                                    email_address=email, 
                                                    last_index = 1)
                    last_sent_email = email
                    last_sent_email_index = list_to_send.index(last_sent_email)
                    break
                
        else:
            last_sent_email_index = list_to_send.index(last_sent_email)
            
               
        for email in (list_to_send[last_sent_email_index:] + list_to_send[:last_sent_email_index]):
            email_id = await self.email_dal.get_email_id(user_id=user_id, 
                                                         email=email)
            if email_id in email_indexes:
                if email not in tmp_list:
                    tmp_list.append(email)
                
                          
        print("tmp_list is", tmp_list)
        
        last_sent_email_index = tmp_list.index(last_sent_email)
        
        if COUNT > len(tmp_list):
            final_list_to_send = tmp_list
            need_to_del = False
        
        elif last_sent_email_index + COUNT > len(tmp_list):
            final_list_to_send = tmp_list[last_sent_email_index:] + tmp_list[:COUNT - len(list_to_send[last_sent_email_index:]) + 1]
            
            
        elif last_sent_email_index + COUNT == len(tmp_list):
            final_list_to_send = tmp_list[last_sent_email_index:]
            final_list_to_send.append(tmp_list[0])
            
        else:
            final_list_to_send = tmp_list[last_sent_email_index:last_sent_email_index + COUNT + 1]
                
                
        await self.email_dal.update_last_sent_index(user_id=user_id, 
                                                    email_address=last_sent_email, 
                                                    last_index = 0)
        await self.email_dal.update_last_sent_index(user_id=user_id, 
                                                    email_address=final_list_to_send[-1], 
                                                    last_index = 1)
        
        print("Список", final_list_to_send)
        
        final_list_to_send = final_list_to_send[0:-1] if need_to_del else final_list_to_send
        
        print("ИТОГОВЫЙ СПИСОК:",final_list_to_send)

        for email in final_list_to_send:
            email_id = await self.email_dal.get_email_id(user_id=user_id, email=email)
            audio_list = await self.audio_dal.get_auto_mailing_audio(user_id=user_id, email_indexes=email_id)
            await self.attach_message(user_id=user_id)
            
            [await self.attach_audio(audio=audio, bot=bot) for audio in audio_list]
            
            try:
                await self.connect(user_id=user_id)
                await self.auto_send_email(user_id=user_id, emails_to=[email])
            except SMTPConnectError:
                await bot.send_message(chat_id=event_chat, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")    
                break 
            except SMTPSenderRefused:
                count = 0
                count += 1
                if count == 0:
                    await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")
                    
                
        await self.email_dal.increment_indexes(user_id=user_id,
                                               emails=final_list_to_send[0:-1])
        

    async def auto_mailing_starter(self, user_id: int, bot: Bot, event_chat: Chat) -> None:
        settings_info = await self.settings_service.get_user_settings_content(user_id)
        current_datetime = datetime.datetime.now()

        combined_datetime = datetime.datetime.combine(current_datetime.date(), settings_info.schedule_time)

        time_difference = combined_datetime - current_datetime
        if abs(time_difference.total_seconds()) >= 1:
            print(time_difference.total_seconds())
        else:
            email_indexes = await self.email_dal.get_email_indexes_to_send(user_id=user_id)
            email_amount = len(email_indexes) if len(email_indexes) > 0 else None
            
            frequency = int(await self.settings_service.get_frequency(user_id))
            current_frequency = int(await self.settings_service.get_current_frequency(user_id))
            schedule_time = await self.settings_service.get_user_scheduler(user_id=user_id)
            
            if not email_amount:
                return await bot.send_message(
                        chat_id=event_chat.id,
                        text='Список доступных почт для отправки закончился. Пополните список почт, либо список аудио')
                
                
            if frequency != current_frequency:
                await self.settings_service.update_settings(user_id=user_id, current_frequency = current_frequency + 1)
                if current_frequency != 0:
                    return await bot.send_message(
                            chat_id=event_chat.id,
                            text=f'До отправления осталось {frequency - current_frequency} дней')
                    
            else:
                try:
                    await self.auto_mailing(user_id=user_id, bot=bot, event_chat=event_chat, email_indexes=email_indexes)
                    await bot.send_message(chat_id=event_chat.id, text=f"Успешно разосланы письма! Следующая рассылка в - {schedule_time}")
                    await self.settings_service.update_settings(user_id,current_frequency = 0)
                    
                    today = datetime.datetime.now().date()
                    next_day = today + datetime.timedelta(days=1)
                    if next_day.month != today.month:
                        next_day = datetime.date(today.year, today.month + 1, 1)
                    run_time = datetime.datetime(next_day.year, next_day.month, next_day.day, 0, 0)
                    
                    self.scheduler.add_job(
                        func=self.settings_service.update_last_update_frequency,
                        trigger='date',
                        run_date=run_time,
                        args=[user_id]
                    )
                except Exception:
                    await bot.send_message(
                        chat_id=event_chat.id,
                        text='Произошла неизвестная ошибка. Обратитесь в поддержку - /support'
                    )
                

    async def turn_on_mailing(self, user_id: int, bot: Bot, event_chat: Chat) -> None:
        schedule_time = await self.settings_service.get_user_scheduler(user_id=user_id)
        audios =  await self.audio_service.get_audio_list(user_id=user_id)
        emails = await self.email_service.get_user_email_list(user_id=user_id)

        if schedule_time:
            try:
                job = self.scheduler.get_jobs()
                print(job)
                if job:
                    self.scheduler.remove_job('MailingService.auto_mailing_starter')
                    
                self.scheduler.add_job(
                    func=self.auto_mailing_starter,
                    trigger="cron",
                    hour=schedule_time.hour,
                    minute=schedule_time.minute,
                    kwargs={'user_id': user_id, 'bot': bot, 'event_chat': event_chat}, 
                    id = 'auto'
                )
                self.scheduler.start()
                await self.settings_service.update_settings(user_id=user_id, is_turned_on=True)

            except SMTPAuthenticationError:
                await bot.send_message(
                    chat_id=event_chat.id,
                    text='Не удалось ауденцифитироваться в вашем аккаунте'
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
        job = self.scheduler.get_job('MailingService.auto_mailing_starter')

        if job:
            self.scheduler.remove_job('MailingService.auto_mailing_starter')
        await self.settings_service.update_settings(user_id=user_id, is_turned_on=False) 
        
        
    async def update_sub_duration(self, user_id: int, bot: Bot):
        sub = await self.user_service.get_sub_duration(user_id)
        if sub >= 0:
            self.scheduler.add_job(
            func=self.user_service.update_sub_duration,
            trigger="cron",
            hour=0,
            minute=0,
            kwargs={'user_id': user_id, 'bot': bot}
        )
            # self.scheduler.start()
            
            
    async def update_email_limit_to_send_for_extra(self, user_id: int, bot: Bot):
        self.scheduler.add_job(
        func=self.user_service.update_email_limit_to_send_for_extra,
        trigger="cron",
        hour=0,
        minute=0,
        kwargs={'user_id': user_id, 'bot': bot}
        )
            
    
    # async def test(self, user_id: int) -> None:
    #     schedule_time = await self.settings_service.get_user_scheduler(user_id=user_id)
    #     print(schedule_time)
    #     print(type(schedule_time))
    #     print(schedule_time.hour)
        
    #     await self.attach_message(user_id=user_id)