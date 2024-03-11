from io import BytesIO

from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

from app.services import UserService, SettingsService

from apscheduler.schedulers.asyncio import AsyncIOScheduler



class MailingService:
    def __init__(
            self,
            settings_service: SettingsService,
            user_service: UserService
    ) -> None:
        self.settings_service = settings_service
        self.user_service = user_service
        self.email_message = MIMEMultipart()
        self.client = SMTP(hostname='smtp.gmail.com', port=587)
        self.scheduler = AsyncIOScheduler()
    

    async def connect(self, user_id: int) -> None:
        user_email = await self.user_service.get_user_personal_email(user_id=user_id)
        password = await self.user_service.get_user_password(user_id=user_id)

        await self.client.connect(
            start_tls=True, validate_certs=False, username=user_email, password=password
        )


    async def attach_audio(self, audio_data: BytesIO, filename: str) -> None:
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
        self.email_message['To'] = ', '.join(emails_to)

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


    async def auto_mailing_verify(self) -> None:
        print("test")


    async def turn_on_scheduler(self, user_id: int) -> None:
        schedule_time = await self.settings_service.get_user_scheduler(user_id=user_id)

        if schedule_time:
            self.scheduler.remove_all_jobs()
            self.scheduler.add_job(
                func=self.auto_mailing_verify,
                trigger="cron",
                hour=12,
                minute=00
            )
            self.scheduler.start()
            await self.settings_service.update_settings(user_id=user_id, is_turned_on=True)

        else:
            raise Exception("Scheduler is not set")


    async def turn_off_scheduler(self, user_id: int) -> None:
        self.scheduler.remove_all_jobs()
        await self.settings_service.update_settings(user_id=user_id, is_turned_on=False) 