from typing import Annotated

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states import RegistrationStatesGroup, AddToEmailStatesGroup, DeletionEmailStatesGroup
from app.bot.utils import (
    get_registration_info,
    get_wait_email_addresses_text,
    get_user_email_addresses
    )
from app.bot.keyboard import inline
from app.services import EmailService

from dishka.integrations.aiogram import inject, Depends

router = Router()


#!Connection to a Gmail Account
@router.callback_query(F.data == "email_account_connection")
async def connect_call(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)

    await query.message.answer(
        text=get_registration_info(),
        disable_web_page_preview=True
        )
    await query.message.answer("Отправь свой Gmail")


#!Deleting Email Addresses
@router.callback_query(F.data == "del_email")
async def del_email(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(f"<b>Напишите почту(ы) которую вы хотите удалить из  списка:</b>")
    await state.set_state(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)


#!Adding Email Addresses
@router.callback_query(F.data == "add_email")
async def handle_audio(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_wait_email_addresses_text())
    await state.clear()
    await state.set_state(AddToEmailStatesGroup.WAIT_FOR_ADD_EMAIL)


#!Editing Email Addresses
@router.callback_query(F.data == "edit_emails")
@inject
async def get_email_list_call(query: CallbackQuery, email_service: Annotated[EmailService, Depends()]) -> None:
    user_id = query.from_user.id
    email_list = await email_service.get_user_email_list(user_id)

    if email_list:
        email_list = "\n".join(email_list)
        await query.message.answer(text=get_user_email_addresses(),
                                   reply_markup=inline.choose_email_action_markup)
        
    else:
        await query.message.answer(text="У вас пока что еще нет почт списке",
                                   reply_markup=inline.add_emails_to_list_markup)
