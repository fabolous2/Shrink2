from typing import Annotated

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.models import User
from app.services import UserService
from app.bot.utils import get_greeting, get_registration_info, get_profile_content, get_not_registered
from app.main.config import ADMIN_ID

from keyboard.inline import profile_inline_kb_markup, registration_mailing_kb_markup, сhoose_mailing_type_kb_markup


commands_router = Router(name=__name__)


@commands_router.message(CommandStart())
@inject
async def start_command_handler(message: Message, user_service: Annotated[UserService, Depends()]) -> None:
    await user_service.save_user(User(user_id=message.from_user.id))
    await message.answer(get_greeting(message.from_user.username))
    # await message.answer(reply_markup=reply.start_markup,disable_web_page_preview=True)


@commands_router.message(Command("register"))
async def register_profile_handler(message: Message, state: FSMContext) -> None:
    await message.answer(get_registration_info(), disable_web_page_preview=True)
    await message.answer("Отправьте свой Gmail")
    # await state.set_state(Reg.email_from)


@commands_router.message(Command("profile"))
@inject
async def profile_content_handler(message: Message, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = message.from_user.id
    email_is_filled = await user_service.user_email_is_filled(user_id)

    if email_is_filled:
        await message.edit_text(get_profile_content(),
                                reply_markup=inline_builder(
                                    ["🧬 Сменить профиль", "⬅ Назад"],
                                    ["quit_profile", "main_menu"],
                                    [1, 1]),
                                disable_web_page_preview=True)
    else:
        await message.answer(get_not_registered(),reply_markup=profile_inline_kb_markup)


#КОММАНДА /SUPPORT
@commands_router.message(Command("support"))
async def cmd_sup(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        await message.answer("АДМИН")
        await state.set_state(Sup.check_admin)
    else:
        await state.set_state(Sup.text)
        await message.answer("""👀 Опиши проблему, которая у тебя возникла ⬇️
<blockquote>Вопросы, предложения, сотрудничество тоже сюда!</blockquote>""")


#КОММАНДА /MAILING
@commands_router.message(Command("mailing"))
async def get_mail(message: Message, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = message.from_user.id
    email_is_filled = await user_service.user_email_is_filled(user_id)

    if email_is_filled:
        await message.answer("📮 Выберите тип рассылки ниже:", reply_markup=сhoose_mailing_type_kb_markup)
        
    else:
        await message.answer(get_not_registered(), reply_markup=registration_mailing_kb_markup)
        