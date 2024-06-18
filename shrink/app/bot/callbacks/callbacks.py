from typing import Annotated

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat
import pytz
from app.models import User, EmailSettings as Settings

import datetime

from app.bot.utils.bot_answer_text import (
    get_advice_for_amount,
    get_advice_for_frequency,
    get_quit_profile,
    get_profile_content,
    get_how_the_bot_works,
    get_pre_quit_text,
    get_mailing_registration_required,
    get_quantity_text,
    get_email_subject_text,
    get_auto_mailing_choice_text,
    get_auto_mailing_settings_info,
    get_email_scheduler_time,
    get_email_description_text,
    get_choose_menu_actions,
    get_successfull_logout,
    get_registration_info, 
    get_support_answer, 
    get_frequency_button,
    get_warning_frequency_text, 
    get_frequency_text,
    get_successful_update_message_text, 
    get_call_support, 
    get_send_gmail
)
from app.bot.keyboard import inline
from app.services import UserService, SettingsService, MailingService, EmailService, AudioService
from app.bot.states import (
    SelfMailingStatesGroup,
    RegistrationStatesGroup,
    EmailContentStatesGroup,
    SupportStatesGroup
)
from app.bot.utils.errors import SchedulerNotSetError, AudioNotAddedError, EmailAudioNotAddedError, EmailNotAddedError

from dishka.integrations.aiogram import inject, Depends

router = Router(name=__name__)


#! Main Menu
@router.callback_query(F.data == "main_menu")
async def menu_call(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        get_choose_menu_actions(),
        chat_id=event_chat.id,
        reply_markup=inline.main_menu_inline_kb_markup,
        message_id=query.message.message_id,   
    )


#! Logout of Profile
@router.callback_query(F.data == "quit_profile")
async def quit_profile_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_quit_profile(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.quit_profile_kb_markup,
        disable_web_page_preview=True
    )


@router.callback_query(F.data == "pre_quit")
async def pre_quit_profile(query: CallbackQuery, bot: Bot) -> None:   
    await bot.edit_message_text(
        text=get_pre_quit_text(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.logout_for_sure_markup
    )


@router.callback_query(F.data == "quit")
@inject
async def quit_profile(
    query: CallbackQuery, bot: Bot,
    user_service: Annotated[UserService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    email_service: Annotated[EmailService, Depends()],
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    user_id = query.from_user.id
    
    await user_service.delete_user_by_user_id(user_id)
    await settings_service.delete_user_by_user_id(user_id)
    await email_service.delete_user_by_user_id(user_id)
    await audio_service.delete_user_by_user_id(user_id)
    

    await bot.edit_message_text(
        text=get_successfull_logout(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.profile_repeat_registration_kb_markup
    )


#! How The Bot Works
@router.callback_query(F.data == "how_works_be_twin")
async def how_works_info_call(query: CallbackQuery) -> None:
    await query.message.edit_text(
        text=get_how_the_bot_works(),
        reply_markup=inline.back_to_main_menu_markup
    )


#! Getting User Profile Content
@router.callback_query(F.data == "profile")
@inject
async def get_user_profile_info(
    query: CallbackQuery,
    user_service: Annotated[UserService, Depends()],
    bot: Bot
) -> None:
    user_id = query.from_user.id
    is_registered = await user_service.user_is_registered(user_id)
    user_email = await user_service.get_user_personal_email(user_id)
    user_subscription = await user_service.user_subscription(user_id)

    if is_registered:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=get_profile_content(
                query.from_user.username,
                user_email,
                user_subscription
            ),
            reply_markup=inline.change_profile_markup,
            disable_web_page_preview=True,
        )

    else:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text=get_mailing_registration_required(),
            reply_markup=inline.profile_inline_kb_markup,
        )


#! Cancel
@router.callback_query(F.data.in_(["cancel", "ok"]))
async def cancel_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
    )


#! Auto-Mailing call
@router.callback_query(F.data == "auto_mailing")
async def auto_mailing_call(query: CallbackQuery, event_chat: Chat, bot: Bot, 
                            state: FSMContext) -> None:
    await state.clear()
    await bot.edit_message_text(
        text=get_auto_mailing_choice_text(),
        chat_id=event_chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.choose_auto_mailing_actions_markup,
    )


@router.callback_query(F.data == "support")
async def support(query: CallbackQuery, event_chat: Chat, bot: Bot, state:FSMContext) -> None:
    await query.message.answer(get_support_answer())
    await state.set_state(SupportStatesGroup.WAIT_FOR_REPORT)


#! Auto-Mailing Settings
@router.callback_query(F.data == "settings")
@inject
async def settings_call(
    query: CallbackQuery,
    bot: Bot,
    settings_service: Annotated[SettingsService, Depends()],
    state: FSMContext
) -> None:
    await state.clear()
    user_id = query.from_user.id
    settings_info = await settings_service.get_user_settings_content(user_id)
    if not settings_info:
        await settings_service.save_user_settings(Settings(user_id=query.message.from_user.id))

    if not settings_info.schedule_time:
        new_schedule_time = datetime.time(hour=19, minute=0)
        settings_info.schedule_time = new_schedule_time
        await settings_service.update_settings(user_id = user_id, schedule_time = settings_info.schedule_time)
            
    await bot.edit_message_text(
        text=get_auto_mailing_settings_info(settings_info),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.turned_off_settings_choice_markup
        if settings_info.is_turned_on
        else inline.turned_on_settings_choice_markup
    )


@router.callback_query(F.data == "set_frequency")
@inject
async def quantity_call(query: CallbackQuery, bot: Bot, 
                        settings_service: Annotated[SettingsService, Depends()]) -> None:
    user_id = query.from_user.id
    is_sent_advice = await settings_service.get_advice_for_frequency(user_id)  
    print(is_sent_advice)  
    if is_sent_advice == 0:
        await query.answer(get_advice_for_frequency(), show_alert=True)
        await settings_service.update_settings(user_id, advice_for_frequency = 1)
        
    await bot.edit_message_text(
        text=get_frequency_button(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id, 
        reply_markup=inline.frequency_kb_markup
        )
    
    
@router.callback_query(F.data.in_(["one_day_frequency", "two_day_frequency", 
                                    "three_day_frequency", "four_day_frequency"]))
@inject
async def frequency(query: CallbackQuery, settings_service: Annotated[SettingsService, Depends()]) -> None:
    current_frequency = await settings_service.get_current_frequency(query.from_user.id)
    frequency_map = {
        'one_day_frequency': 1,
        'two_day_frequency': 2,
        'three_day_frequency': 3,
        'four_day_frequency': 4
    }
    
    selected_frequency = frequency_map[query.data]
    if selected_frequency == 1:
        output_frequency = "ежедневно"
    elif selected_frequency == 2:
        output_frequency = get_frequency_text(2)
    elif selected_frequency == 3:
        output_frequency = get_frequency_text(3)
    else:
        output_frequency = get_frequency_text(4)
        
    if current_frequency > selected_frequency:
        await settings_service.update_settings(user_id=query.from_user.id, current_frequency=selected_frequency)
        await query.message.answer(user_id=query.from_user.id,
                               text=get_warning_frequency_text(selected_frequency))
    
    await settings_service.update_settings(user_id=query.from_user.id, frequency=selected_frequency)
    await query.answer(f"Периодичность обновлена: {output_frequency}")
        

@router.callback_query(F.data == "set_quantity")
@inject
async def quantity_call(query: CallbackQuery, bot: Bot, settings_service: Annotated[SettingsService, Depends()]) -> None:
    user_id = query.from_user.id
    is_sent_advice = await settings_service.get_advice_for_quantity(user_id)  
    if is_sent_advice == 0:
        await query.answer(get_advice_for_amount(), show_alert=True)
        await settings_service.update_settings(user_id, advice_for_quantity = 1)
    
    await bot.edit_message_text(
        text=get_quantity_text(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id ,
        reply_markup=inline.audio_amount_kb_markup
    )
    
    
@router.callback_query(F.data == "set_scheduler")
async def mail_time_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_email_scheduler_time(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.schedular_kb_markup
    )
    
     
@router.callback_query(F.data.in_(["two_audio_amount", "three_audio_amount", 
                                    "four_audio_amount", "five_audio_amount"]))
@inject
async def scheduler(query: CallbackQuery, state: FSMContext, bot: Bot, 
                    settings_service: Annotated[SettingsService, Depends()]) -> None:
    
    user_id = query.from_user.id
    frequency_map = {
        'two_audio_amount': "2",
        'three_audio_amount': "3",
        'four_audio_amount': '4',
        'five_audio_amount': "5"
    }
    selected_amount = frequency_map[query.data]
    amount = int(selected_amount)

    await settings_service.set_amount(user_id=user_id, amount=amount)
    await query.answer(f"Количество аудио в одном письме обновлено: {amount}")


@router.callback_query(F.data == "set_email_content")
async def desc_call(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await query.message.edit_text(get_email_subject_text(), 
                         reply_markup=inline.subject_kb_markup)
    await state.set_state(EmailContentStatesGroup.WAIT_FOR_SUBJECT)
    
    
@router.callback_query(F.data == "without_subject", EmailContentStatesGroup.WAIT_FOR_SUBJECT)
@inject
async def desc_call_without_subj(query: CallbackQuery, state: FSMContext,
                                settings_service: Annotated[SettingsService, Depends()]) -> None:
    await state.clear()
    try:
        await settings_service.update_settings(
            user_id=query.from_user.id,
            email_subject = None
        )
        await query.message.edit_text(text=get_successful_update_message_text(), 
                                      reply_markup=inline.back_from_update_message_kb_markup)

    except Exception:
        await query.message.answer( 
            get_call_support()
        )
    

@router.callback_query(F.data == "set_description")
async def desc_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.edit_text(get_email_description_text(), 
                         reply_markup=inline.desc_kb_markup)
    await state.set_state(EmailContentStatesGroup.WAIT_FOR_DESCRIPTION)   
    
    
@router.callback_query(F.data == "without_desc", EmailContentStatesGroup.WAIT_FOR_DESCRIPTION)
@inject
async def desc_call(query: CallbackQuery, state: FSMContext, 
                    settings_service: Annotated[SettingsService, Depends()]) -> None:
    await state.clear()
    try:
        await settings_service.update_settings(
            user_id=query.from_user.id,
            email_text= None
        )
        await query.message.edit_text(text=get_successful_update_message_text(), 
                                      reply_markup=inline.back_from_update_message_kb_markup)

    except Exception:
        await query.message.answer(
            get_call_support()
        )


@router.callback_query(F.data == "set_scheduler")
async def mail_time_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_email_scheduler_time(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.schedular_kb_markup
    )
    
     
@router.callback_query(F.data.in_(["seven_pm", "eight_pm", 
                                    "nine_pm", "ten_pm", 
                                    "pm"]))
@inject
async def scheduler(query: CallbackQuery, bot: Bot, 
                    settings_service: Annotated[SettingsService, Depends()],
                    mailing_service: Annotated[MailingService, Depends()],
                    event_chat: Chat) -> None:
    user_id = query.from_user.id
    user_settings = await settings_service.get_user_settings_content(user_id=user_id)
    current_time = datetime.datetime.now()
    

    updated_time = current_time + datetime.timedelta(minutes=5)
    updated_time_str = updated_time.strftime('%H:%M')    
    frequency_map = {
        'seven_pm': "19:00",
        'eight_pm': "20:00",
        'nine_pm': '21:00',
        'ten_pm': "22:00",
        'pm': updated_time_str
    }
    
    selected_schedule_time = frequency_map[query.data]
    schedule_time = datetime.datetime.strptime(selected_schedule_time, "%H:%M").time() 
    
    await settings_service.update_settings(user_id=query.from_user.id, schedule_time=schedule_time)
    await query.answer(f"Время отправки обновлено: {schedule_time}")
    if user_settings.is_turned_on:
        await mailing_service.turn_on_mailing(user_id=user_id, bot=bot, event_chat=event_chat)
    

@router.callback_query(F.data == "self_mailing")
async def self_mailing_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.edit_text(text=get_email_subject_text(), 
                         reply_markup=inline.subject_for_extra_kb_markup)
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_SUBJECT)


@router.callback_query(F.data.in_(['repeat_registration', 'registration']))
@inject
async def connect_call(query: CallbackQuery, state: FSMContext,
                       user_service: Annotated[UserService, Depends()],
                       settings_service: Annotated[SettingsService, Depends()]) -> None:
    await user_service.save_user(User(user_id=query.from_user.id))
    await settings_service.save_user_settings(Settings(user_id=query.from_user.id))
    
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)
    await query.message.edit_text(text=get_registration_info(),
                               disable_web_page_preview=True)
    await query.message.answer(get_send_gmail())


@router.callback_query(F.data == "turn_on_mailing")
@inject
async def turn_on_mailing_call(
    query: CallbackQuery,
    mailing_service: Annotated[MailingService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    bot: Bot,
    event_chat: Chat
) -> None:
    user_id = query.from_user.id
    user_settings = await settings_service.get_user_settings_content(user_id=user_id)
    current_frequency = user_settings.frequency
    if current_frequency == 1:
        selected_frequency = 'Ежедневно'
    else:
        selected_frequency = f'Раз в {current_frequency} дня'
    
    try:
        await mailing_service.turn_on_mailing(user_id=user_id, bot=bot, event_chat=event_chat)
        await bot.edit_message_text(
            text=get_auto_mailing_settings_info(user_settings),
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=inline.turned_off_settings_choice_markup
        )
        await query.answer(f"Вы включили авто-рассылку!\n({selected_frequency} в {user_settings.schedule_time})")

    except SchedulerNotSetError:
        await query.answer("У вас не установлено время отправки!")
    except EmailNotAddedError:
        await query.answer("Добавьте почты!")
    except AudioNotAddedError:
        await query.answer("Добавьте аудио!")
    except EmailAudioNotAddedError:
        await query.answer("Добавьте аудио и почты получателей!")



@router.callback_query(F.data == "turn_off_mailing")
@inject
async def turn_off_mailing_call(
    query: CallbackQuery,
    mailing_service: Annotated[MailingService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    bot: Bot
) -> None:
    user_id = query.from_user.id
    user_settings = await settings_service.get_user_settings_content(user_id=user_id)

    await mailing_service.turn_off_scheduler(user_id=user_id)
    await bot.edit_message_text(
        text=get_auto_mailing_settings_info(user_settings),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.turned_on_settings_choice_markup
    )
    await query.answer("Вы выключили авто-рассылку")
