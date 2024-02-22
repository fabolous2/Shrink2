from typing import Annotated

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Chat
from aiogram.filters import ExceptionMessageFilter

from app.bot.utils import (
    get_quit_profile,
    get_profile_content,
    get_registration_info,
    get_how_the_bot_works,
    get_reg_start_info,
    get_without_sub_info,
    get_basic_sub_info,
    get_premium_sub_info,
    get_basic_subscription_price,
    get_premium_subscription_price,
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
)
from app.bot.keyboard import inline
from app.services import UserService
from app.bot.states import (
    RegistrationStatesGroup,
    AddAudiosStatesGroup,
    DelAudioStatesGroup,
    SelfMailingStatesGroup,
    SendingEmailSchecule,
    EmailQuantityStatesGroup,
    DescriptionStatesGroup,
)

from dishka.integrations.aiogram import inject, Depends

router = Router()


#! Main Menu
@router.callback_query(F.data == "main_menu")
async def menu_call(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        "🔮Выберите действия по кнопкам ниже:",
        chat_id=event_chat.id,
        reply_markup=inline.main_menu,
        message_id=query.message.message_id,
        
    )


#! Logout of Profile
@router.callback_query(F.data == "quit_profile")
async def quit_profile(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        get_quit_profile(),
        chat_id=event_chat.id,
        disable_web_page_preview=True,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.quit_profile_kb_markup,
    )


@router.callback_query(F.data == "pre_quit")
async def pre_quit_profile(query: CallbackQuery, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_pre_quit_text(),
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.log_out_for_sure_button,
    )

@router.callback_query(F.data == "quit")
async def quit_profile(
    query: CallbackQuery, bot: Bot, user_service: Annotated[UserService, Depends()]
) -> None:
    await user_service.delete_user_by_user_id(query.from_user.id)
    await bot.edit_message_text(
        text="""Вы успешно вышли из аккаунта! 🪫\nЖелаете создать новый?""",
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.profile_repeat_registration_kb_markup,
    )


#! How The Bot Works
@router.callback_query(F.data == "how_work")
async def how_work_call(query: CallbackQuery) -> None:
    await query.message.edit_text(
        get_how_the_bot_works(), reply_markup=inline.back_to_main_menu_markup
    )


#! Getting User Profile Content
@router.callback_query(F.data == "profile")
async def get_user_profile_info(
    query: CallbackQuery, user_service: Annotated[UserService, Depends()]
) -> None:
    is_register = await user_service.user_email_and_password_is_set(query.from_user.id)

    if is_register:
        await query.message.edit_text(
            get_profile_content(),
            reply_markup=inline.change_profile_markup,
            disable_web_page_preview=True,
        )

    else:
        await query.message.edit_text(
            get_mailing_registration_required(),
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
async def auto_mailing_call(query: CallbackQuery, bot: Bot) -> None:
    await bot.edit_message_text(
        text=get_auto_mailing_choice_text(),
        chat_id=query.chat_instance,
        message_id=query.message.message_id,
        inline_message_id=query.inline_message_id,
        reply_markup=inline.choose_auto_mailing_actions_markup,
    )


#! Auto-Mailing Settings
@router.callback_query(F.data == "settings")
async def settings_call(
    query: CallbackQuery, user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = query.from_user.id
    info = user_service.get_user_personal_email(user_id)

    await query.message.edit_text(
        get_auto_mailing_settings_info(), reply_markup=inline.settings_choice_markup
    )


@router.callback_query(F.data == "quantity")
async def quantity_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_quantity_text())
    await state.set_state(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)


@router.callback_query(F.data == "description")
async def desc_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_email_subject_text())
    await state.set_state()


@router.callback_query(F.data == "mail_time")
async def mail_time_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_email_scheduler_time())
    await state.set_state(SendingEmailSchecule.WAIT_FOR_TIME)


#! Self-Mailing
@router.callback_query(F.data == "self_mailing")
async def self_mailing_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_wait_email_addresses_text())
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_EMAILS)


#! Audio-list Actions
@router.callback_query(F.data == "add_audio")
async def add_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_add_audio_text())
    await state.set_state(AddAudiosStatesGroup.WAIT_FOR_AUDIOS)


@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_del_audio_text())
    await state.set_state(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL)
