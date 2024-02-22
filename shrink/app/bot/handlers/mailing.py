from aiogram import Router,F,Bot
from aiogram.types import Message
from aiogram_album import AlbumMessage
from aiogram.fsm.context import FSMContext
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from database.database import (get_email_from,get_pwd_from,update_get_email_to_list,
                               update_audio_file,get_email_to_list,get_audio_file,get_head_desc,update_email_value,update_audio_value,get_quantity)
from utils.states import Mailing
from keyboards import reply

router=Router()

async def test_conn_open(conn):
    try:
        status = conn.noop()[0]
    except:
        status = -1
    return True if status == 250 else False

async def send_email(conn, email_from,msg,password,to_email,audio_info,bot):
    text_message = """those beats are free for non-profit use that means u can use them for free on soundcloud but if u want to drop a song on all platforms u should buy a license 
        to buy dm me on IG: @nemxxo_"""
    if not test_conn_open(conn):
        conn.starttls()
        conn.login(email_from, password)
        for audio in audio_info:
            filename = audio[1]
            audio_file_info = await bot.get_file(audio[0])
            audio_file_path = audio_file_info.file_path
            audio_data = await bot.download_file(audio_file_path)
            file = MIMEBase('audio', 'mp3')
            file.set_payload(audio_data.read())
            encoders.encode_base64(file)
            file.add_header('content-disposition', 'attachment', filename=filename)
            msg.attach(file)

    conn.sendmail(email_from, to_email, msg.as_string())
    return conn

async def connect_gmail(email_from,password):
    s = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    s.starttls()
    s.login(email_from, password)
    return s

async def get_audio_info(messages)->list:
    files_data = {}
    audio_info = []
    for m in messages:
        files_data["file_id"] = m.audio.file_id
        files_data["name"] = m.audio.file_name.replace(" ", "")
        audio_info.append(files_data["file_id"] + ' ' + files_data['name'])
    return audio_info

async def attach_email(audio_info:list,bot,msg)->None:
    for audio in audio_info:
        filename = audio[1]
        audio_file_info = await bot.get_file(audio[0])
        audio_file_path = audio_file_info.file_path
        audio_data = await bot.download_file(audio_file_path)
        file = MIMEBase('audio', 'mp3')
        file.set_payload(audio_data.read())
        encoders.encode_base64(file)
        file.add_header('content-disposition','attachment',filename=filename)
        msg.attach(file)

async def sending_email(message,email_from,email_to_list,msg,conn)->None:
    conn.sendmail(email_from, email_to_list, msg.as_string())
    await message.answer("Аудиофайл(ы) успешно отправлены на указанные адреса", reply_markup=reply.start_markup)


#САМОСТОЯТЕЛЬНАЯ РАССЫЛКА
@router.message(Mailing.self_mailing,F.media_group_id,flags={'chat_action':'upload_audio'})
async def album_handler(messages: AlbumMessage,bot:Bot,state:FSMContext):
    data=await state.get_data()
    await state.clear()

    data=[email for email in data.values()]
    email_to_list='\n'.join(data).split()
    text_message ='None'
    message = None
    audio_info = None
    for m in messages:
        message = m
        audio_info = await get_audio_info(messages)
    email_from = get_email_from(message.from_user.id)
    password = get_pwd_from(message.from_user.id)

    audio_info = list(map(lambda x: x.split(), audio_info))
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['Subject'] = "new fire beat. you need to check it out..."
    msg['To'] = ','.join(email_to_list)
    msg.attach(MIMEText(text_message, 'plain'))

    await attach_email(audio_info,bot,msg)
    s = await connect_gmail(email_from,password)
    await sending_email(message=message,email_from=email_from,email_to_list=email_to_list,msg=msg,conn=s)


@router.message(F.media_group_id)
async def auto_mailing(message: Message,bot: Bot):
    user_id = message.from_user.id
    audio_info = get_audio_file(user_id)
    quantity=await get_quantity(user_id)

    if audio_info:
        audio_info = list(map(lambda x: x.split(), audio_info.split('\n')))
        email_to_list = get_email_to_list(user_id)
        print(len(audio_info)//quantity)
        print(email_to_list)
        email_to_list=list(filter(lambda email: len(audio_info)//quantity > int(email[-1]), email_to_list))
        await update_email_value(user_id)
        print(email_to_list)

        # email_from = get_email_from(user_id)
        # password = get_pwd_from(user_id)
        # text, subject = get_head_desc(user_id)
        #
        # msg = MIMEMultipart()
        # msg['From'] = email_from
        # msg['Subject'] = subject
        # msg['To'] = ', '.join(email_to_list)
        # msg.attach(MIMEText(text, 'plain'))
        #
        # await attach_email(audio_info, bot, msg)
        # conn = await connect_gmail(email_from, password)
        #
        # # try:
        # await sending_email(message=message, email_from=email_from, email_to_list=email_to_list, msg=msg, conn=conn)
        # await update_email_value(user_id)
        # await update_audio_value(user_id)
        # # except Exception:
        # #     await message.answer("Что то пошло не так. Возможно вы превысили общий размер аудио.")
        #

