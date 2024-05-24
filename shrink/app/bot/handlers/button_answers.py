from typing import Annotated

from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.services import UserService

from app.bot.states import SupportStatesGroup
from app.bot.utils.bot_answer_text import (
    get_auto_mailing_choice_text, get_support_answer, get_mailing_registration_required,
    get_choose_type_of_mailing, get_main_menu_text
)

from app.bot.keyboard import inline

router = Router(name=__name__)


@router.message(F.text == "‍👨‍💻 Поддержка")
async def support_button_answer_handler(
    message: Message, state: FSMContext,
) -> None:
    await state.clear()
    await message.answer(get_support_answer())
    await state.set_state(SupportStatesGroup.WAIT_FOR_REPORT)


@router.message(F.text == "📨 Рассылка")
@inject
async def mailing_button_answer_handler(message: Message, user_service: Annotated[UserService, Depends()], 
                                        bot: Bot, state: FSMContext) -> None:
    await state.clear()
    registered = await user_service.user_is_registered(message.from_user.id)
    subscription = await user_service.user_subscription(message.from_user.id)
    
    if not registered:
        await message.answer(
            text=get_mailing_registration_required(), 
            reply_markup=inline.reg_for_first_time_mailing_kb_markup,
        )

    else:
        if subscription != "free":
            await message.answer(get_choose_type_of_mailing(),
                                reply_markup=inline.choose_mailing_type_kb_markup)
        else:
            await bot.send_message(
            message.from_user.id,
            text=get_auto_mailing_choice_text(),
            reply_markup=inline.choose_auto_mailing_actions_markup
        )


@router.message(F.text == "🎡 Главное меню")
@inject
async def main_menu_answer_handler(message: Message, 
                                   state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        get_main_menu_text(), 
        reply_markup=inline.main_menu_inline_kb_markup,
    )

    
