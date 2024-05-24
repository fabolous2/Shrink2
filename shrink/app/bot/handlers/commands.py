import re
from typing import Annotated

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from dishka.integrations.aiogram import inject, Depends
from app.models import User, EmailSettings as Settings
from app.services import UserService, SettingsService, EmailService, AudioService, MailingService
from app.bot.utils.bot_answer_text import (
    get_auto_mailing_choice_text,
    get_call_support,
    get_email_description_text,
    get_empty_audio_list,
    get_empty_email_list,
    get_greeting,
    get_limit_email_list,
    get_registration_info,
    get_profile_content,
    get_not_registered,
    get_successful_update_message_text,
    get_successful_update_value,
    get_support_answer,
    get_user_email_addresses, 
    get_send_gmail,
    get_choose_type_of_mailing,
    get_wait_email_addresses_text,
    get_wait_to_del_email_addresses
)
from app.bot.states import (
    SupportStatesGroup,
    RegistrationStatesGroup,
    EmailQuantityStatesGroup,
    EmailContentStatesGroup,
    AddToEmailStatesGroup,
    DeletionEmailStatesGroup,
    SelfMailingStatesGroup
)
from app.bot.keyboard import inline
from app.bot.keyboard import reply


commands_router = Router(name=__name__)


async def delete_messages(chat_id, message_ids, bot):
    await bot.delete_messages(chat_id, message_ids)


@commands_router.message(CommandStart())
@inject
async def start_command_handler(
    message: Message,
    user_service: Annotated[UserService, Depends()],
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    await user_service.save_user(User(user_id=message.from_user.id))
    await settings_service.save_user_settings(Settings(user_id=message.from_user.id))       

    await message.answer(
        get_greeting(message.from_user.first_name),
        reply_markup=reply.main_menu_keyboard_markup,
        disable_web_page_preview=True,
    )


#! Starting Registration Process
@commands_router.message(Command("register"))
@inject
async def register_profile_handler(message: Message, state: FSMContext, 
                                   user_service: Annotated[UserService, Depends()]) -> None:
    user_id = message.from_user.id
    is_registered = await user_service.user_is_registered(user_id)
    
    if is_registered:
        await message.answer("Вы уже зарегестрировались")
    else:
        await message.answer(get_registration_info(), disable_web_page_preview=True)
        await message.answer(get_send_gmail())
        await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)


@commands_router.message(Command("profile"))
@inject
async def profile_content_handler(
    message: Message, user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    is_registered = await user_service.user_is_registered(user_id)
    email = await user_service.get_user_personal_email(user_id=user_id)
    subscription = await user_service.user_subscription(user_id)

    if is_registered:
        await message.answer(
            get_profile_content(
                first_name=message.from_user.first_name,
                email=email,
                subscription=subscription,
            ),
            reply_markup=inline.change_profile_markup,
            disable_web_page_preview=True,
        )

    else:
        await message.answer(
            get_not_registered(), reply_markup=inline.profile_inline_kb_markup
        )


@commands_router.message(Command("support"))
async def support_handler(message: Message, state: FSMContext) -> None:
    await message.answer(get_support_answer())
    await state.set_state(SupportStatesGroup.WAIT_FOR_REPORT)


#! /Mailing
@commands_router.message(Command("mailing"))
@inject
async def mailing_type_handler(
    message: Message, user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_and_password_is_filled = await user_service.user_is_registered(user_id)      
    
    if email_and_password_is_filled:
        subscription = await user_service.user_subscription(user_id)
        if subscription == 'free':
            text = "📮 Выберите действия по кнопкам ниже:"
            reply_markup_for_mailing = inline.choose_auto_mailing_actions_markup
        else: 
            text = get_choose_type_of_mailing()
            reply_markup_for_mailing = inline.choose_mailing_type_kb_markup
        await message.answer(
            text = text,
            reply_markup=reply_markup_for_mailing
        )

    else:
        await message.answer(
            get_not_registered(), reply_markup=inline.registration_mailing_kb_markup
        )


@commands_router.message(EmailContentStatesGroup.WAIT_FOR_SUBJECT, ~F.content_type.in_({'text'}))
@inject
async def set_subject_invalid_content(message: Message) -> None:
    await message.answer("Пожалуйста, введите текст.")


@commands_router.message(EmailContentStatesGroup.WAIT_FOR_SUBJECT, F.content_type == ContentType.TEXT)
@inject
async def set_subject(message: Message, state: FSMContext,
                      settings_service: Annotated[SettingsService, Depends()], 
                      bot: Bot) -> None:
    await state.clear()
    text = message.text 
    description = await settings_service.get_user_mail_text(message.from_user.id)
    if description:
        total_len = len(text)+len(description)
    else:
        total_len = len(text)
        
    if total_len < 3500:
        try:
            await settings_service.update_settings(
                user_id=message.from_user.id,
                email_subject=message.text
            )
            last_message_id = message.message_id - 1
            await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
            await message.answer(get_successful_update_message_text(), 
                                reply_markup=inline.back_from_update_message_kb_markup)

        except Exception:
            await message.answer(
                get_call_support()
            )
    else:
        await message.answer("Ваш загловок письма и текст в сумме не должны превышать 3500 символов!")
        
        
@commands_router.message(EmailContentStatesGroup.WAIT_FOR_DESCRIPTION, ~F.content_type.in_({'text'}))
@inject
async def set_description_invalid_content(message: Message) -> None:
    await message.answer("Пожалуйста, введите текст.")
    

@commands_router.message(EmailContentStatesGroup.WAIT_FOR_DESCRIPTION, F.content_type == ContentType.TEXT)
@inject
async def set_description(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()],
    bot: Bot
) -> None:
    await state.clear()
    text = message.text 
    subject = await settings_service.get_user_mail_subject(message.from_user.id)
    if subject:
        total_len = len(text)+len(subject)
    else:
        total_len = len(text)
        
    if total_len < 3500:
        try:
            await settings_service.update_settings(
                user_id=message.from_user.id,
                email_text=message.text,
            )
            last_message_id = message.message_id - 1
            await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
            await message.answer(get_successful_update_message_text(), 
                                reply_markup=inline.back_from_update_message_kb_markup)

        except Exception:
            await message.answer(get_call_support())
    else:
        await message.answer("Ваш загловок письма и текст в сумме не должны превышать 3500 символов!")

@commands_router.message(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)
@inject
async def set_quantity(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()],
) -> None:
    amount = message.text
    user_id = message.from_user.id

    int(amount)
    await settings_service.set_amount(user_id=user_id, amount=amount)
    await message.answer(get_successful_update_value())
    await state.clear()


@commands_router.message(AddToEmailStatesGroup.WAIT_FOR_ADD_EMAIL)
@inject
async def handle_audio(
    message: Message,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()],
    user_service: Annotated[UserService, Depends()],
    bot: Bot
) -> None:
    await state.clear()
    user_id = message.from_user.id
    email_from_db = await email_service.get_user_email_list(user_id)
    email_limit = await user_service.get_email_limit(user_id)
    
    
    text = message.text
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    emails = list(set(emails))
    print(emails)
    count = 0
    last_message_id = message.message_id - 1
    await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
    
    if email_from_db:
        email_from_db = email_from_db.split('\n')
    if not emails:
        await message.answer("Упс... Что-то пошло не так. Возможно почты введены неверно")
        
    else:   
        if len(email_from_db) + len(emails) > email_limit:
            await message.answer(get_limit_email_list(email_limit, len(email_from_db)))
        
        else:
            emails_list = []
            if email_from_db:
                for email in emails:
                    count = 0
                    for email_db in email_from_db:
                        if email_db != email:
                            count += 1
      
                    if count == len(email_from_db):        
                        email_dict = {"user_id": user_id, "email_address": email}
                        emails_list.append(email_dict)
                            
            else:
                for email in emails:
                    email_dict = {"user_id": user_id, "email_address": email}
                    emails_list.append(email_dict)
                
            try:
                await email_service.update_email_list(emails_list)
                await message.answer(
                    f"✅ Вы успешно добавили почты ({len(emails_list)})",
                    reply_markup=inline.view_email_list_kb_markup)
                
            except Exception:
                await message.answer("Упс... Что-то пошло не так. Возможно почты введены неверно")
        

@commands_router.message(Command("email_list"))
@inject
async def get_email_list(
    message: Message, email_service: Annotated[EmailService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_list = await email_service.get_user_email_list(user_id=user_id)

    if email_list:
        await message.answer(
            get_user_email_addresses(email_list=email_list),
            reply_markup=inline.choose_email_action_markup,
        )

    else:
        await message.answer(
            get_empty_email_list(),
            reply_markup=inline.add_emails_to_list_markup,
        )


# DEL EMAIL from EMAIL LIST
@commands_router.message(Command("del_emails"))
async def del_email(message: Message, state: FSMContext):
    await message.answer(
        get_wait_to_del_email_addresses()
    )
    await state.set_state(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)


@commands_router.message(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)
@inject
async def email_del(
    message: Message,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()],
    bot: Bot
) -> None:
    await state.clear()
    
    user_id = message.from_user.id
    text = message.text
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    if not emails:
        await message.answer("Упс... Что-то пошло не так. Возможно почты введены неверно")
        
    else:
        for email in emails:
            email_id = await email_service.get_last_sent_by_email(user_id=user_id, 
                                                                  email=email)
            if email_id == 1:
                list_to_send = await email_service.get_user_emails(user_id=user_id)          
                email_index  = list_to_send.index(email)
                if emails[-1] == list_to_send[-1]:
                    await email_service.update_last_sent_index(user_id,       
                                                           list_to_send[0], 1)
                else:
                    await email_service.update_last_sent_index(user_id,       
                                                           list_to_send[email_index + len(emails) - (email_index - len(list_to_send[:email_index]))], 1)
            
        
        emails_to_del_list = [{"user_id": user_id, "to": email} for email in emails]
        to_list = [email['to'] for email in emails_to_del_list]
        
        deleted_count = await email_service.get_count_matching_emails(user_id ,to_list)

        try:
            await email_service.delete_emails_by_address(to_list)
            last_message_id = message.message_id - 1
            await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
            await message.answer(
                f"✅ Вы успешно избавились от почт ({deleted_count})", 
                reply_markup=inline.view_email_list_kb_markup
        )
        except Exception:
            await message.answer("Упс... Что-то пошло не так. Возможно почты введены неверно")
            
                
@commands_router.message(Command("audio_list"))
@inject                                                                                                                                 
async def get_audio_list_call(
    message: Message,
    audio_service: Annotated[AudioService, Depends()],
    bot: Bot
) -> None:
    user_id = message.from_user.id
    audio_list = await audio_service.get_audio_list(user_id)
    audio_list = [audio.file_id for audio in audio_list]

    if audio_list:
        chunks = [audio_list[i : i + 10] for i in range(0, len(audio_list), 10)]
        await message.answer("Вот ваш список аудио:")

        for audio_chunk in chunks:
            media_group = MediaGroupBuilder()
            [media_group.add_audio(media=audio) for audio in audio_chunk]

            await bot.send_media_group(user_id, media_group.build())

        await message.answer(
            get_auto_mailing_choice_text(),
            reply_markup=inline.choose_audio_actions_kb_markup,
        )

    else:
        await message.answer(
            get_empty_audio_list(), reply_markup=inline.add_audio_kb_markup
        )


@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_SUBJECT, ~F.content_type.in_({'text'}))
async def get_wrong_for_subj_for_mailing(message: Message) -> None:
    await message.answer("Пожалуйста, введите текст.")


@commands_router.callback_query(F.data == 'without_subject_for_extra')
@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_SUBJECT, F.content_type  == ContentType.TEXT)
async def get_subject_for_mailing(message: Message, state: FSMContext, 
                                  bot: Bot) -> None:
    if isinstance(message, CallbackQuery): 
        await state.update_data(subject=None)
        await message.message.delete()
    else:  
        text = message.text
        await state.update_data(subject=text)
        last_message_id = message.message_id - 1
        await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
    await bot.send_message(chat_id=message.from_user.id,
                           text=get_email_description_text(), 
                         reply_markup=inline.desc_for_extra_kb_markup)
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_TEXT)


@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_TEXT, ~F.content_type.in_({'text'}))
async def get_wrong_for_text_for_mailing(message: Message) -> None:
    await message.answer("Пожалуйста, введите текст.")


@commands_router.callback_query(F.data == 'without_desc_for_extra')
@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_TEXT, F.content_type == ContentType.TEXT)
async def get_text_for_mailing(message: Message, state: FSMContext, 
                                  bot: Bot) -> None:
    if isinstance(message, CallbackQuery): 
        await state.update_data(desc=None)
        await message.message.delete()
    else:  
        text = message.text
        await state.update_data(desc=text)
        last_message_id = message.message_id - 1
        await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
    await bot.send_message(chat_id=message.from_user.id,
                           text=get_wait_email_addresses_text())
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_EMAILS)


@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_EMAILS)
async def get_audio_for_mailing(message: Message, state: FSMContext, 
                                bot: Bot) -> None: 
    text = message.text
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if not emails:
        await message.answer(text="❗️Что-то пошло не так. Возможно вы неверно ввели почты получателей.")
    else:
        last_message_id = message.message_id - 1
        await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
        await state.update_data(emails_for_extra=message.text.replace(' ', '').replace(',', '\n'))
        await message.answer("🎵 Отправьте биты")
        await state.set_state(SelfMailingStatesGroup.WAIT_FOR_AUDIOS)


@commands_router.message(Command('test'))
@inject
async def test_bot(message: Message, service: Annotated[MailingService, Depends()]) -> None:
    await service.test(user_id=message.from_user.id)