from typing import Annotated

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.services import UserService

from app.bot.states import SupportStatesGroup
from app.bot.utils import get_support_answer, get_mailing_registration_required

from app.bot.keyboard import inline

router = Router(name=__name__)

@router.message(F.text == "‍👨‍💻 Поддержка")
async def support_button_answer_handler(
    message: Message, state: FSMContext,
) -> None:
    await message.answer(get_support_answer())
    await state.set_state(SupportStatesGroup.WAIT_FOR_REPORT)


@router.message(F.text == "📨 Рассылка")
@inject
async def mailing_button_answer_handler(message: Message, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    email_and_password_is_set = await user_service.user_email_and_password_is_set(message.from_user.id)

    if not email_and_password_is_set:
        await message.answer(
            get_mailing_registration_required(), 
            reply_markup=inline.registration_mailing_kb_markup,
        )

    else:
        await message.answer()


@router.message(F.text == "🎡 Главное меню")
@inject
async def main_menu_answer_handler(message: Message) -> None:
    await message.answer(
        "🔮 Выберите действия по кнопкам ниже:", 
        reply_markup=inline.main_menu_inline_kb_markup,
    )

    
