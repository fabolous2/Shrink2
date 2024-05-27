from typing import Annotated

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from app.bot.states import RegistrationStatesGroup, AddToEmailStatesGroup, DeletionEmailStatesGroup
from app.bot.utils.bot_answer_text import (
    get_registration_info,
    get_wait_email_addresses_text,
    get_user_email_addresses, 
    get_send_gmail, 
    get_wait_to_del_email_addresses,
    get_empty_email_list
    )
from app.bot.keyboard import inline
from app.services import EmailService

from dishka.integrations.aiogram import inject, Depends

router = Router() 

PAGE_SIZE = 150


@router.callback_query(F.data == "email_account_connection")
async def account_connection_call(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)

    await query.message.answer(
        text=get_registration_info(),
        disable_web_page_preview=True
        )
    await query.message.answer(get_send_gmail())


@router.callback_query(F.data == "delete_emails")
async def deletion_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.edit_text(get_wait_to_del_email_addresses())
    await state.set_state(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)


@router.callback_query(F.data == "add_emails")
@inject
async def add_email_list_to_db(
    query: CallbackQuery,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()]
) -> None:
    user_id = query.from_user.id
    email_list = await email_service.available_email_list(user_id=user_id)
    
    
    if email_list:
        pages = [email_list[i:i + PAGE_SIZE] for i in range(0, len(email_list), PAGE_SIZE)]
        page_count = len(pages)
        
        await state.update_data(pages=pages)
        await show_email_page(query.message, pages, 0, page_count)

    else:
        await query.message.edit_text(
            get_empty_email_list(),
            reply_markup=inline.add_emails_to_list_markup
        )
        

async def show_email_page(message, pages, current_page, page_count):
    email_list = '\n'.join(pages[current_page])
    keyboard = inline.paginator_email(current_page, page_count, pages)
    
    additional_buttons = [inline.add_emails_button, inline.delete_emails_button]
    back_button = [inline.back_to_settings_menu]
    
    new_keyboard = keyboard.inline_keyboard + [additional_buttons] + [back_button]

    if message.text:
        await message.edit_text(
            text=f"{get_user_email_addresses(email_list=email_list)}",
           reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
    )
    else:
        await message.answer(
            text=get_user_email_addresses(email_list=email_list),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=new_keyboard)
        )
        
    
@router.callback_query(F.data.startswith("pag:"))
async def handle_pagination_action(query: CallbackQuery, state: FSMContext):
    data = query.data.split(":")[-1] 
    action, current_page, page_count = data.split(",")[:3] 
    current_page = int(current_page)
    page_count = int(page_count)

    state_data = await state.get_data()
    pages = state_data.get("pages")

    if action == 'prev':
        current_page -= 1
    elif action == 'next':
        current_page += 1

    await show_email_page(query.message, pages, current_page, page_count)
    

@router.callback_query(F.data == "add_emails_to_db")
async def add_email(query: CallbackQuery, state: FSMContext):
    await query.message.edit_text(get_wait_email_addresses_text())
    await state.clear()
    await state.set_state(AddToEmailStatesGroup.WAIT_FOR_ADD_EMAIL)


@router.callback_query(F.data == "edit_emails")
@inject
async def edition_emails_call(query: CallbackQuery, email_service: Annotated[EmailService, Depends()]) -> None:
    user_id = query.from_user.id
    email_list = await email_service.get_user_email_list(user_id)

    if email_list:
        email_list = "\n".join(email_list)
        await query.message.answer(text=get_user_email_addresses(),
                                   reply_markup=inline.choose_email_action_markup)
        
    else:
        await query.message.answer(text=get_empty_email_list(),
                                   reply_markup=inline.add_emails_to_list_markup)
