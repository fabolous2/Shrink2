from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.states import RegistrationStatesGroup
from app.bot.utils import get_registration_info, get_wait_email_addresses_text

router = Router()

#Email Actions

#!Connection to a Gmail Account
@router.callback_query(F.data == "email_account_connection")
async def connect_call(query: CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)
    await query.message.answer(get_registration_info(),
                               disable_web_page_preview=True)
    
    await query.message.answer("Отправь свой Gmail")


#!Deleting Email Addresses
@router.callback_query(F.data == "del_email")
async def del_email(query: CallbackQuery, state: FSMContext):
    await query.message.answer(f"<b>Напишите почту которую вы хотите удалить из  списка:</b>")
    await state.set_state(Del_email.email)


#!Adding Email Addresses
@router.callback_query(F.data == "add_email")
async def handle_audio(query: CallbackQuery, state: FSMContext):
    await query.message.answer(get_wait_email_addresses_text())
    await state.clear()
    await state.set_state(Send.send_gmail)


#!Editing Email Addresses
@router.callback_query(F.data == "edit_emails")
async def get_email_list_call(query: CallbackQuery):
    user_id = query.from_user.id

    if get_email_to_list(user_id):
        emails = await get_email_to_list(user_id).replace(' ', '').split()
        emails = "\n".join(emails)
        await query.message.answer(f"Вот ваш актуальный список почт:\n\n{emails}",
                                   reply_markup=inline_builder(
                                       ["Удалить почту(ы)", "Добавить почту(ы)"],
                                       ["del_email", "add_email"]
                                   ))
    else:
        await query.message.answer("У вас пока что еще нет почт списке(", reply_markup=inline_builder(
            ["Добавить почту"],
            ["add_email"]
        ))

