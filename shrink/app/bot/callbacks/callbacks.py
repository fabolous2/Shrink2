from typing import Annotated

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat

from app.bot.utils import (
    get_quit_profile,
    get_profile_content,
    get_how_the_bot_works,
    get_pre_quit_text,
    get_mailing_registration_required,
    get_wait_email_addresses_text,
    get_quantity_text,
    get_email_subject_text,
    get_add_audio_text,
    get_auto_mailing_choice_text,
    get_auto_mailing_settings_info,
    get_del_audio_text,
    get_email_scheduler_time,
    get_choose_menu_actions,
    get_successfull_logout,
    get_registration_info
)
from app.bot.keyboard import inline
from app.services import UserService, SettingsService, MailingService
from app.bot.states import (
    SelfMailingStatesGroup,
    EmailQuantityStatesGroup,
    RegistrationStatesGroup,
    EmailContentStatesGroup,
    EmailScheduleStatesGroup
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
    # await query.message.edit_text(
    #     text=get_quit_profile(),
    #     reply_markup=inline.quit_profile_kb_markup,
    #     disable_web_page_preview=True
    # )

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
    query: CallbackQuery, bot: Bot, user_service: Annotated[UserService, Depends()]
) -> None:
    await user_service.delete_user_by_user_id(query.from_user.id)

    await bot.edit_message_text(
        text=get_successfull_logout(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.profile_repeat_registration_kb_markup
    )


#! How The Bot Works
@router.callback_query(F.data == "how_works_be_twin")
async def how_works_info_call(query: CallbackQuery, bot: Bot) -> None:
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
            text=get_mailing_registration_required(),
            reply_markup=inline.profile_inline_kb_markup,
        )


#! Cancel
@router.callback_query(F.data == "cancel")
async def cancel_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.delete_message(
        chat_id=query.chat_instance,
        message_id=query.message.message_id,
    )


#! Auto-Mailing call
@router.callback_query(F.data == "auto_mailing")
async def auto_mailing_call(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_auto_mailing_choice_text(),
        chat_id=event_chat.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.choose_auto_mailing_actions_markup,
    )


#! Auto-Mailing Settings
@router.callback_query(F.data == "settings")
@inject
async def settings_call(
    query: CallbackQuery,
    bot: Bot,
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    user_id = query.from_user.id
    settings_info = await settings_service.get_user_settings_content(user_id)

    await bot.edit_message_text(
        text=get_auto_mailing_settings_info(settings_info),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.turned_off_settings_choice_markup
        if settings_info.is_turned_on
        else inline.turned_on_settings_choice_markup
    )


@router.callback_query(F.data == "set_quantity")
async def quantity_call(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_quantity_text(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    await state.set_state(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)


@router.callback_query(F.data == "set_email_content")
async def desc_call(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_email_subject_text(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    await state.set_state(EmailContentStatesGroup.WAIT_FOR_SUBJECT)


@router.callback_query(F.data == "set_scheduler")
async def mail_time_call(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_email_scheduler_time(),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    await state.set_state(EmailScheduleStatesGroup.WAIT_FOR_TIME)


#! Self-Mailing
@router.callback_query(F.data == "self_mailing")
async def self_mailing_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_wait_email_addresses_text())
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_EMAILS)


#EMAIL CONNECTION
@router.callback_query(F.data.in_(['repeat_registration', 'registration']))
async def connect_call(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)
    await query.message.answer(text=get_registration_info(),
                               disable_web_page_preview=True)
    await query.message.answer("Отправь свой Gmail")


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

    # try:
    await mailing_service.turn_on_mailing(user_id=user_id, bot=bot, event_chat=event_chat)
    await bot.edit_message_text(
        text=get_auto_mailing_settings_info(user_settings),
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=inline.turned_off_settings_choice_markup
    )
    await query.answer(f"Вы успешно включили авто-рассылку!\n(Ежедневно в {user_settings.schedule_time})")

    # except SchedulerNotSetError:
    #     await query.answer("У вас не установлено время отправки!")
    # except EmailNotAddedError:
    #     await query.answer("Добавьте почты!")
    # except AudioNotAddedError:
    #     await query.answer("Добавьте аудио!")
    # except EmailAudioNotAddedError:
    #     await query.answer("Добавьте аудио и почты получателей!")

    # except Exception as _ex:
    #     print(_ex)
    #     await query.answer("Упс...Что-то пошло не так :(")


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
    await query.answer("Вы успешно выключили авто-рассылку")
