from aiogram import Bot
from aiogram.types import Message
from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase


class MailingService:
    def __init__(self, hostname: str, port: int) -> None:
        self.client = SMTP(hostname=hostname, port=port)


    async def login(self, user_email: str, password: str) -> None:
        await self.client.starttls()
        await self.client.login(user_email=user_email, password=password)
    

    async def attach_audio(self, audio_list: list, bot: Bot, email_message: MIMEMultipart) -> None:
        for audio in audio_list:
            filename = audio['filename']

            #Загружаем аудио
            audio_file_info = await bot.get_file(audio['file_id'])
            audio_file_path = audio_file_info.file_path
            audio_data = await bot.download_file(audio_file_path)

            file = MIMEBase('audio', 'mp3')
            file.set_payload(audio_data.read())
            encoders.encode_base64(file)

            file.add_header('content-disposition','attachment', filename=filename)
            email_message.attach(file)#прикрпепляем к письму аудио файл

    
    async def sending_email(self, email_from: str, emails_to: str, email_message: MIMEMultipart) -> None:
        await self.client.sendmail(email_from, emails_to, email_message.as_string())


    async def get_email_message_content(
            email_from: str,
            emails_to: list,
            user_text_message: str,
            email_subject: str
    ) -> MIMEMultipart:
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['Subject'] = email_subject
        email_message['To'] = ','.join(emails_to)
        email_message.attach(MIMEText(user_text_message, 'plain'))

        return email_message
    

    async def conduct_audio_info(audio_messages) -> list:
        audio_info = []
        for audio in audio_messages:
            files_data = {
                'file_id': audio.audio.file_id,
                'filename': audio.audio.file_name
            }
            # audio_info.append(files_data["file_id"] + ' ' + files_data['name'])
            audio_info.append(files_data)
            return audio_info