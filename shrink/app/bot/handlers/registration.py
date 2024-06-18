from typing import Annotated
import re

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.models import User
from app.services import UserService
from app.bot.states import RegistrationStatesGroup
from app.bot.utils import get_if_wrong_password, get_profile_content, Encryption
from app.bot.keyboard import inline


router = Router()


@router.message(RegistrationStatesGroup.WAIT_FOR_EMAIL)
async def email_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    email_reg = message.text
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if not re.match(email_pattern, email_reg):
        await message.answer("Почта введена неверно. Попробуйте еще раз!")
        return

    await state.update_data(email_from=message.text)
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_PASSWORD)

    await bot.send_message(
        message.from_user.id, text="Отлично! Теперь введите пароль приложения"
    )


@router.message(RegistrationStatesGroup.WAIT_FOR_PASSWORD)
@inject
async def password_handler(
    message: Message,
    state: FSMContext,
    user_service: Annotated[UserService, Depends()],
    encryption: Annotated[Encryption, Depends()]
) -> None:
    password = message.text
    user_id = message.from_user.id
    exists = await user_service.exists(user_id)
    if (
        len(password) < 19
        or len(password) > 20
        or re.search(r"\d", password)
        or not password.count(" ") == 3
    ):
        await message.answer(
            get_if_wrong_password(), reply_markup=inline.profile_inline_kb_markup
        )
        await state.clear()
    encrypted_password, secret = encryption.encrypt(password=password)

    await state.update_data(password=password)
    data = await state.get_data()
    if not exists:
        await user_service.save_user(User(user_id=message.from_user.id))
        
    await user_service.update_user(
        user_id=user_id,
        personal_email=data["email_from"],
        password=encrypted_password,
        subscription ='NOT_SUBSCRIBED',
        secret=secret
    )
    await message.answer("Поздравляю, вы успешно вошли в аккаунт!")
    await message.answer(
            text=get_profile_content(
            first_name=message.from_user.first_name,
            email=data["email_from"],
            subscription="free"
        ),
        reply_markup=inline.change_profile_markup,
        disable_web_page_preview=True,
    )
    await state.clear()
