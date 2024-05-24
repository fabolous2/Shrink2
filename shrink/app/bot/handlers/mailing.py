import hashlib
import re
from aiosmtplib import SMTPConnectError, SMTPSenderRefused
from typing import Annotated

from aiogram import Bot, Router, F
from aiogram.types import ContentType, Chat, User, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram_album import AlbumMessage

from aiosmtplib import SMTPConnectError, SMTPSenderRefused

from app.bot.keyboard import inline

from app.bot.states import SelfMailingStatesGroup
from app.services import EmailService, AudioService, MailingService

from dishka.integrations.aiogram import inject, Depends

from app.bot.utils.bot_answer_text import get_call_support, get_extra_menu, get_successful_send_audio
from app.services.settings_service import SettingsService
from app.bot.handlers.commands import delete_messages


router = Router()

PAGE_SIZE = 8


async def show_extra_audio_page(message, audio_list, current_page, page_count, user_data, query=None):
    start_index = current_page * PAGE_SIZE
    end_index = min((current_page + 1) * PAGE_SIZE, len(audio_list))
    subject = user_data['subject']
    desc = user_data['desc']

    audio_chunk = audio_list[start_index:end_index]

    buttons = []
    for audio_info in audio_chunk:
        print(audio_info)
        file_id = audio_info['file_id']
        unique_id = hashlib.md5(file_id.encode()).hexdigest()
        audio_info['unique_id'] = unique_id
        buttons.append([InlineKeyboardButton(text=audio_info['audio_title'], callback_data=f"play_audio:{unique_id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    keyboard.inline_keyboard.append([inline.add_beats_to_state, inline.send_from_state])

    if query:  
        await query.message.edit_text(
            get_extra_menu(subject, desc),
            reply_markup=keyboard
        )
    else:  
        await message.answer(
            get_extra_menu(subject, desc),
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("play_audio:"))
@inject
async def send_audio_callback(query: CallbackQuery, state: FSMContext):
    unique_id = query.data.split(":")[-1]
    state_data = await state.get_data()
    audio_list = state_data.get("audio_list")
    file_id = find_file_id_by_unique_id(audio_list, unique_id)
    if file_id:
        await query.message.answer_audio(file_id)
    else:
        await query.message.answer("Аудиофайл не найден.")
        
        
def find_file_id_by_unique_id(audio_list, unique_id):
    print('audio_list is', audio_list)
    for audio_info in audio_list:
        if audio_info.get('unique_id') == unique_id:
            return audio_info.get('file_id')
    return None
    

@router.callback_query(F.data.startswith("pag_extra_audio:"))
async def handle_extra_audio_pagination_action(query: CallbackQuery, state: FSMContext):
    data = query.data.split(":")[-1] 
    action, current_page, page_count = data.split(",")[:3] 
    current_page = int(current_page)
    page_count = int(page_count)

    state_data = await state.get_data()
    audio_list = state_data.get("audio_list")

    if action == 'prev':
        current_page -= 1
    elif action == 'next':
        current_page += 1

    await show_extra_audio_page(query.message, audio_list, current_page, page_count, query)


async def display_and_send_extra_audio_list(audio_list, message, query):
    page_count = (len(audio_list) + PAGE_SIZE - 1) // PAGE_SIZE
    await show_extra_audio_page(message, audio_list, 0, page_count, query)


@router.callback_query(F.data == 'add_to_db') 
@inject
async def get_audio_for_mailing(query: CallbackQuery, state: FSMContext) -> None: 
    await query.message.edit_text("🎵 Отправьте биты")
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_AUDIOS)


@router.message(
    SelfMailingStatesGroup.WAIT_FOR_AUDIOS,
    F.media_group_id,
    flags={'chat_action': 'upload_document'}
)
@inject
async def self_mailing_handler(
    audio_messages: AlbumMessage,
    audio_service: Annotated[AudioService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    user_data = await state.get_data()
    LIMIT = await settings_service.get_email_limit_to_send_for_extra(audio_messages.from_user.id)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    user_id = audio_messages.from_user.id
    user_data_string = '\n'.join([str(value) for value in user_data.values()])
    
    audio_list = await audio_service.create_audio_list_extra(user_id=user_id, album_message=audio_messages, is_extra=1)

    emails = re.findall(email_pattern, user_data_string)
    
    if not user_data_string:
        await state.update_data(emails=emails)
    
    if len(emails) > LIMIT:
        await bot.send_message(chat_id=event_chat.id, text=f"Количество почт ({len(emails)}) превышает допустимый лимит - {LIMIT}") 
        await state.clear()  

    else:
        try:
            await audio_service.add_audio(audio_list=audio_list)
            extra_audio_list = await audio_service.get_audio_list(user_id, is_extra=1)

            unique_audio_set = set()  
            unique_extra_audio_list = []  
            
            for audio in extra_audio_list:
                if audio.name not in unique_audio_set:
                    unique_audio_set.add(audio.name)
                    unique_extra_audio_list.append({'file_id': audio.file_id, 'audio_title': audio.name})

            if unique_extra_audio_list:
                page_count = (len(unique_extra_audio_list) + PAGE_SIZE - 1) // PAGE_SIZE
                
                for audio_info in unique_extra_audio_list:
                    file_id = audio_info.get('file_id')
                    unique_id = hashlib.md5(file_id.encode()).hexdigest()
                    audio_info['unique_id'] = unique_id

                await state.update_data(audio_list=unique_extra_audio_list)
                await show_extra_audio_page(audio_messages, unique_extra_audio_list, 0, page_count, user_data)
                         
        except Exception as _ex:
            print(_ex)
            await audio_messages.answer(get_call_support())

    
@router.message(SelfMailingStatesGroup.WAIT_FOR_AUDIOS, ~F.content_type.in_({'audio'}))
async def incorrect_file_format(
    message: Message,
) -> None:
    await message.answer("Вы отправили неверный формат файла. Оправлять можно только аудио")
    
    
@router.message(
        SelfMailingStatesGroup.WAIT_FOR_AUDIOS,
        F.content_type == ContentType.AUDIO,
        flags={'chat_action': 'upload_document'}
)
@inject
async def self_mailing_one_audio(
    audio_message: Message,
    audio_service: Annotated[AudioService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    user_data = await state.get_data()
    LIMIT = await settings_service.get_email_limit_to_send_for_extra(audio_message.from_user.id)
    print(LIMIT)
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    user_id = audio_message.from_user.id
    user_data_string = '\n'.join([str(value) for value in user_data.values()])
    print("user_data_string", user_data.values())

    emails = re.findall(email_pattern, user_data_string)
    print(emails)
    last_message_id = audio_message.message_id - 1
    await delete_messages(audio_message.chat.id, [last_message_id - 1, last_message_id, audio_message.message_id], bot)
    
    if not user_data_string:
        await state.update_data(emails=emails)

    if len(emails) > LIMIT:
        await bot.send_message(chat_id=event_chat.id, text=f"Количество почт ({len(emails)}) превышает допустимый лимит - {LIMIT}") 
        await state.clear()
    
    else:  
        audio_list = {
        'audio_id': audio_message.audio.file_id,
        'audio_name': audio_message.audio.file_name,
        'size': audio_message.audio.file_size,
        'user_id': audio_message.from_user.id,
        'audio_index': 0, 
        'is_extra': 1
    }
        await audio_service.add_audio(audio_list=audio_list)
        
        try:
            extra_audio_list = await audio_service.get_audio_list(user_id, is_extra=1)

            unique_audio_set = set()  
            unique_extra_audio_list = []  
            
            for audio in extra_audio_list:
                if audio.name not in unique_audio_set:
                    unique_audio_set.add(audio.name)
                    unique_extra_audio_list.append({'file_id': audio.file_id, 'audio_title': audio.name})

            if unique_extra_audio_list:
                page_count = (len(unique_extra_audio_list) + PAGE_SIZE - 1) // PAGE_SIZE
                
                for audio_info in unique_extra_audio_list:
                    file_id = audio_info.get('file_id')
                    unique_id = hashlib.md5(file_id.encode()).hexdigest()
                    audio_info['unique_id'] = unique_id

                await state.update_data(audio_list=unique_extra_audio_list)
                await show_extra_audio_page(audio_message, unique_extra_audio_list, 0, page_count, user_data)     
        except Exception:
            await bot.send_message(chat_id=event_chat.id, text=get_call_support())
        
        
@router.callback_query(F.data == 'send_from_db')
@router.message(SelfMailingStatesGroup.WAIT_FOR_AUDIOS)        
@inject
async def extra_send_beats(query: CallbackQuery, mailing_service: Annotated[MailingService, Depends()],
    audio_service: Annotated[AudioService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    state: FSMContext,
    bot: Bot,
    event_chat: Chat) -> None:
    
    await query.message.answer("Идет отправка...")
    user_id = query.from_user.id
    LIMIT = await settings_service.get_email_limit_to_send_for_extra(user_id)
    user_data = await state.get_data()
    subject = user_data['subject']
    desc = user_data['desc']
    emails_for_extra = user_data['emails_for_extra']
    count = 0
    
    filtered_list = []
    audio_names_to_check = set()
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    audio_messages = await audio_service.get_audio_list(user_id=user_id, 
                                                        is_extra=1)
    
    for audio in audio_messages:
            if audio.name not in audio_names_to_check:
                audio_names_to_check.add(audio.name)
                filtered_list.append(audio)
    audio_messages = filtered_list
    emails = re.findall(email_pattern, emails_for_extra)
    
    await settings_service.update_settings(user_id, email_limit_to_send_for_extra = LIMIT - len(emails))

    for email in emails:
        await mailing_service.attach_message_for_extra(subject, desc)
        [await mailing_service.attach_audio(audio=audio, bot=bot) for audio in audio_messages]
        
        try:
            await mailing_service.connect(user_id=user_id)
            await mailing_service.auto_send_email(user_id=user_id, emails_to=[email])
        except SMTPConnectError:
                await bot.send_message(chat_id=event_chat.id, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")  
                 
        except SMTPSenderRefused:
                count = len(emails)
                await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")
                break  
        # except SMTPAuthenticationError:
        #     count += 1
        #     await bot.send_message(chat_id=event_chat.id, text=get_call_support())        
                  
    if count < len(emails):
        await bot.send_message(chat_id=event_chat.id, text=get_successful_send_audio())
    await audio_service.delete_extra_audio(user_id)
    await state.update_data(emails=[])
    await state.clear()


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

    await mailing_service.attach_audio(audio_list=audio_list, bot=bot)

    try:
        await mailing_service.connect(user_id=user_id)
        await mailing_service.send_email(user_id=user_id, emails_to=emails_to)
        await bot.send_message(chat_id=event_chat.id, text="Аудиофайл(ы) успешно отправлены на указанные адреса")

    except SMTPConnectError:
        await bot.send_message(chat_id=event_chat.id, text="Произошла ошибка при подключении к вашему аккаунту. Попробуйте еще раз или перерегистрируйте аккаунт")     
    except SMTPSenderRefused:
        await bot.send_message(chat_id=event_chat.id, text="Ваше сообщение превысило ограничения размера сообщения Google. За подробной информацией - https://support.google.com/mail/?p=MaxSizeError")
    

async def auto_mailing_verify() -> None:
    print("заработал")