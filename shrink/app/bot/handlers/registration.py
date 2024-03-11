from typing import Annotated
import re

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.models import User
from app.services import UserService
from app.bot.states import RegistrationStatesGroup
from app.bot.utils import get_if_wrong_password, get_profile_content
from app.bot.keyboard import inline

from dishka.integrations.aiogram import inject, Depends

router = Router()


@router.message(RegistrationStatesGroup.WAIT_FOR_EMAIL)
async def get_user_email(message: Message, state: FSMContext, bot: Bot) -> None:
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
async def get_user_password(
    message: Message, state: FSMContext, user_service: Annotated[UserService, Depends()]
) -> None:
    password = message.text
    user_id = message.from_user.id
    subscription = await user_service.user_subscription(user_id=user_id)

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

    await state.update_data(password=password)
    data = await state.get_data()

    formatted_text = [] 
    [formatted_text.append(value) for key, value in data.items()]

    await user_service.update_user(
        user_id=user_id,
        personal_email=formatted_text[0],
        password=formatted_text[1],
    )
    # //await update_get_pwd_from(message.from_user.id,formatted_text[1])
    # //await update_get_email_from(user_id, formatted_text[0])

    await message.answer("Поздравляю, вы успешно вошли в аккаунт!")
    await message.answer(
        text=get_profile_content(
            first_name=message.from_user.first_name,
            email=formatted_text[0],
            subscription=subscription
        ),
        reply_markup=inline.change_profile_markup,
        disable_web_page_preview=True,
    )

    await state.clear()
