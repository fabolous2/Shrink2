import re
from datetime import datetime
from typing import Annotated

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart,Command
from aiogram.fsm.context import FSMContext

from dishka.integrations.aiogram import inject, Depends

from app.models import User, EmailSettings as Settings, UserEmail
from app.services import UserService, SettingsService, EmailService
from app.bot.utils import (
    get_greeting,
    get_registration_info,
    get_profile_content,
    get_not_registered,
    get_support_answer,
    get_user_email_addresses
    )
from app.main.config import ADMIN_ID

from app.bot.states import (
    SupportStatesGroup,
    RegistrationStatesGroup,
    EmailQuantityStatesGroup,
    EmailScheduleStatesGroup,
    EmailContentStatesGroup,
    AddToEmailStatesGroup,
    DeletionEmailStatesGroup
)

from app.bot.keyboard import inline
from app.bot.keyboard import reply


commands_router = Router(name=__name__)

#! /Start
@commands_router.message(CommandStart())
@inject
async def start_command_handler(
    message: Message,
    user_service: Annotated[UserService, Depends()],
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    await user_service.save_user(User(user_id=message.from_user.id))
    await settings_service.save_user_settings(Settings(user_id=message.from_user.id))

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
async def profile_content_handler(
    message: Message,
    state: FSMContext,
    user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    is_registered = await user_service.user_email_and_password_is_set(user_id)
    email = await user_service.get_user_personal_email(user_id=user_id)
    subscription = await user_service.user_subscription(user_id)

    if is_registered:
        await message.answer(get_profile_content(
            first_name=message.from_user.first_name,
            email=email,
            subscription=subscription
),
        reply_markup=inline.change_profile_markup,
        disable_web_page_preview=True)

    else:
        await message.answer(get_not_registered(),
                             reply_markup=inline.profile_inline_kb_markup)


#! /Support
@commands_router.message(Command("support"),  F.text.lower() == "поддержка")
async def support_handler(message: Message, state: FSMContext) -> None:
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
async def mailing_type_handler(
    message: Message,
    user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_and_password_is_filled = await user_service.user_email_and_password_is_set(user_id)

    if email_and_password_is_filled:
        await message.answer("📮 Выберите тип рассылки ниже:",
                             reply_markup=inline.сhoose_mailing_type_kb_markup)
        
    else:
        await message.answer(get_not_registered(),
                             reply_markup=inline.registration_mailing_kb_markup)
        

@commands_router.message(EmailContentStatesGroup.WAIT_FOR_SUBJECT)
async def set_subject(message: Message, state: FSMContext) -> None:
    await state.update_data(header=message.text)
    await message.answer("Отлично! Теперь придумайте описание к вашему письму")
    await state.set_state(EmailContentStatesGroup.WAIT_FOR_DESCRIPTION)


@commands_router.message(EmailContentStatesGroup.WAIT_FOR_DESCRIPTION)
@inject
async def set_description(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    await state.update_data(description=message.text)
    data = await state.get_data()
    await state.clear()

    try:
        await settings_service.update_settings(
            user_id=message.from_user.id,
            email_subject=data["header"],
            email_text=data["description"]
        )
        await message.answer("Вы успешно обновили своё письмо")

    except Exception:
        await message.answer("Что то пошло не так,попробуйте обратиться в поддержку - /support")
    

@commands_router.message(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)
@inject
async def set_quantity(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    quantity = message.text
    user_id = message.from_user.id

    try:
        int(quantity)

        await settings_service.update_settings(
            user_id=user_id,
            quantity=quantity
        )
        await message.answer("Вы успешно установили значение!")
        await state.clear()
        
    except Exception:
        await message.answer("Отправьте число!")


@commands_router.message(EmailScheduleStatesGroup.WAIT_FOR_TIME)
@inject
async def get_mail_time(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()]
) -> None:
    pattern = r'^\d+\d[:]\d+\d$'

    if not re.match(pattern, message.text):
        await message.answer("Время введено неверно. Попробуйте еще раз!")

    try:
        # Convert the message.text string to a time object
        schedule_time = datetime.strptime(message.text, '%H:%M').time()

        # Update the settings with the converted time object
        await settings_service.update_settings(
            user_id=message.from_user.id,
            schedule_time=schedule_time
        )

        await message.answer("Вы успешно установили время отправки!")
        await state.clear()

    except ValueError:
        await message.answer("Ошибка при конвертации времени. Попробуйте еще раз!")


# Emails Additing
@commands_router.message(AddToEmailStatesGroup.WAIT_FOR_ADD_EMAIL)
@inject
async def handle_audio(
    message: Message,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()]
) -> None:
    await state.clear()
    email_to = message.text.replace(' ', '').split(',')
    user_id = message.from_user.id

    email_to_list = []
    for email in email_to:
        email_dict = {
            "user_id": user_id,
            "to": email
        }
        email_to_list.append(email_dict)

    await email_service.update_email_list(email_to_list)
    await message.answer("Отлично, ты добавил новые почты!\n Чтобы посмотреть актуальный список почт"
                         " - воспользуйтесь \n/email_list")



@commands_router.message(Command("email_list"))
@inject
async def get_email_list(
    message: Message,
    email_service: Annotated[EmailService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_list = await email_service.get_user_email_list(user_id=user_id)
    print(email_list)
    if email_list:
        await message.answer(get_user_email_addresses(email_list=email_list),
                             reply_markup=inline.choose_email_action_markup)

    else:
        await message.answer("У вас пока что еще нет почт списке(",
                             reply_markup=inline.add_emails_to_list_markup)


#DEL EMAIL from EMAIL LIST
@commands_router.message(Command("del_emails"))
async def del_email(message: Message, state: FSMContext):
    await message.answer(f"<b>Напишите почту(ы) которую вы хотите удалить из  списка:</b>")
    await state.set_state(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)


#TODO: удаление почт
@commands_router.message(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)
@inject
async def email_del(
    message: Message,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()]
) -> None:
    emails_to_del = message.text.replace(' ', '').split(',')
    user_id = message.from_user.id

    emails_to_del_list = [
        {"user_id": user_id, "to": email}
        for email in emails_to_del
    ]

    await email_service.delete_emails(emails_to_del_list)

    try:
        await message.answer("Отлично, ты успешно удалил почты!\n Чтобы посмотреть актуальный список почт"
                             " - воспользуйтесь \n/email_list")

    except Exception:
        await message.answer("Упс... Что-то пошло не так. Возможно такой почты не существует в вашем списке или произошла ошибка")

    await state.clear()