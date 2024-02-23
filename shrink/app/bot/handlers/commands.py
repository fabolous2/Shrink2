from typing import Annotated

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.models import User
from app.services import UserService
from app.bot.utils import (
    get_greeting,
    get_registration_info,
    get_profile_content,
    get_not_registered,
    get_support_answer
    )
from app.main.config import ADMIN_ID

from app.bot.states import SupportStatesGroup, RegistrationStatesGroup

from app.bot.keyboard import inline
from app.bot.keyboard import reply


commands_router = Router(name=__name__)

#! /Start
@commands_router.message(CommandStart())
@inject
async def start_command_handler(message: Message, user_service: Annotated[UserService, Depends()]) -> None:
    await user_service.save_user(User(user_id=message.from_user.id))
    await message.answer(get_greeting(message.from_user.username),
                         reply_markup=reply.main_menu_keyboard_markup,
                         disable_web_page_preview=True)


#! Starting Registration Process
@commands_router.message(Command("register"))
async def register_profile_handler(message: Message, state: FSMContext) -> None:
    await message.answer(get_registration_info(),
                         disable_web_page_preview=True)
    
    await message.answer("Отправьте свой Gmail")
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)


#! Getting Profile Content
@commands_router.message(Command("profile"))
@inject
async def profile_content_handler(message: Message, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = message.from_user.id
    email_and_password_is_filled = await user_service.user_email_and_password_is_set(user_id)

    if email_and_password_is_filled:
        await message.edit_text(get_profile_content(),
                                reply_markup=inline.change_profile_markup,
                                disable_web_page_preview=True)
    else:
        await message.answer(get_not_registered(),
                             reply_markup=inline.profile_inline_kb_markup)


#! /Support
@commands_router.message(Command("support"),  F.text.lower() == "поддержка")
async def cmd_sup(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await message.answer("АДМИН")
        await state.set_state(SupportStatesGroup.ADMIN_CHECKING)

    else:
        await state.set_state(SupportStatesGroup.WAIT_FOR_REPORT)
        await message.answer(get_support_answer)


#! /Mailing
@commands_router.message(Command("mailing"))
@inject
async def get_mail(message: Message, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = message.from_user.id
    email_and_password_is_filled = await user_service.user_email_and_password_is_set(user_id)

    if email_and_password_is_filled:
        await message.answer("📮 Выберите тип рассылки ниже:",
                             reply_markup=inline.сhoose_mailing_type_kb_markup)
        
    else:
        await message.answer(get_not_registered(),
                             reply_markup=inline.registration_mailing_kb_markup)
        