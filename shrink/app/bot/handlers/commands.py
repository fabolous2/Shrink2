import re
from datetime import datetime
from typing import Annotated

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from dishka.integrations.aiogram import inject, Depends

from app.models import User, EmailSettings as Settings
from app.services import UserService, SettingsService, EmailService, AudioService
from app.bot.utils import (
    get_greeting,
    get_registration_info,
    get_profile_content,
    get_not_registered,
    get_support_answer,
    get_user_email_addresses,
)
from app.main.config import ADMIN_ID

from app.bot.states import (
    SupportStatesGroup,
    RegistrationStatesGroup,
    EmailQuantityStatesGroup,
    EmailScheduleStatesGroup,
    EmailContentStatesGroup,
    AddToEmailStatesGroup,
    DeletionEmailStatesGroup,
    SelfMailingStatesGroup
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
    settings_service: Annotated[SettingsService, Depends()],
) -> None:
    await user_service.save_user(User(user_id=message.from_user.id))
    await settings_service.save_user_settings(Settings(user_id=message.from_user.id))

    await message.answer(
        get_greeting(message.from_user.username),
        reply_markup=reply.main_menu_keyboard_markup,
        disable_web_page_preview=True,
    )


#! Starting Registration Process
@commands_router.message(Command("register"))
async def register_profile_handler(message: Message, state: FSMContext) -> None:
    await message.answer(get_registration_info(), disable_web_page_preview=True)

    await message.answer("Отправьте свой Gmail")
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_EMAIL)


#! Getting Profile Content
@commands_router.message(Command("profile"))
@inject
async def profile_content_handler(
    message: Message, user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    is_registered = await user_service.user_email_and_password_is_set(user_id)
    email = await user_service.get_user_personal_email(user_id=user_id)
    subscription = await user_service.user_subscription(user_id)

    if is_registered:
        await message.answer(
            get_profile_content(
                first_name=message.from_user.first_name,
                email=email,
                subscription=subscription,
            ),
            reply_markup=inline.change_profile_markup,
            disable_web_page_preview=True,
        )

    else:
        await message.answer(
            get_not_registered(), reply_markup=inline.profile_inline_kb_markup
        )


#! /Support
@commands_router.message(Command("support"), F.text.lower() == "поддержка")
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
    message: Message, user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_and_password_is_filled = await user_service.user_email_and_password_is_set(
        user_id
    )

    if email_and_password_is_filled:
        await message.answer(
            "📮 Выберите тип рассылки ниже:",
            reply_markup=inline.сhoose_mailing_type_kb_markup
        )

    else:
        await message.answer(
            get_not_registered(), reply_markup=inline.registration_mailing_kb_markup
        )


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
    settings_service: Annotated[SettingsService, Depends()],
) -> None:
    await state.update_data(description=message.text)
    data = await state.get_data()
    await state.clear()

    try:
        await settings_service.update_settings(
            user_id=message.from_user.id,
            email_subject=data["header"],
            email_text=data["description"],
        )
        await message.answer("Вы успешно обновили своё письмо")

    except Exception:
        await message.answer(
            "Что то пошло не так,попробуйте обратиться в поддержку - /support"
        )


@commands_router.message(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)
@inject
async def set_quantity(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()],
) -> None:
    quantity = message.text
    user_id = message.from_user.id

    try:
        int(quantity)

        await settings_service.update_settings(user_id=user_id, quantity=quantity)
        await message.answer("Вы успешно установили значение!")
        await state.clear()

    except Exception:
        await message.answer("Отправьте число!")


@commands_router.message(EmailScheduleStatesGroup.WAIT_FOR_TIME)
@inject
async def get_mail_time(
    message: Message,
    state: FSMContext,
    settings_service: Annotated[SettingsService, Depends()],
) -> None:
    pattern = r"^\d+\d[:]\d+\d$"

    if not re.match(pattern, message.text):
        await message.answer("Время введено неверно. Попробуйте еще раз!")

    try:
        # Convert the message.text string to a time object
        schedule_time = datetime.strptime(message.text, "%H:%M").time()

        # Update the settings with the converted time object
        await settings_service.update_settings(
            user_id=message.from_user.id, schedule_time=schedule_time
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
    email_service: Annotated[EmailService, Depends()],
) -> None:
    await state.clear()
    email_to = message.text.replace(" ", "").split(",")
    user_id = message.from_user.id

    email_to_list = []
    for email in email_to:
        email_dict = {"user_id": user_id, "to": email}
        email_to_list.append(email_dict)

    await email_service.update_email_list(email_to_list)
    await message.answer(
        "Отлично, ты добавил новые почты!\n Чтобы посмотреть актуальный список почт"
        " - воспользуйтесь \n/email_list"
    )


@commands_router.message(Command("email_list"))
@inject
async def get_email_list(
    message: Message, email_service: Annotated[EmailService, Depends()]
) -> None:
    user_id = message.from_user.id
    email_list = await email_service.get_user_email_list(user_id=user_id)
    print(email_list)
    if email_list:
        await message.answer(
            get_user_email_addresses(email_list=email_list),
            reply_markup=inline.choose_email_action_markup,
        )

    else:
        await message.answer(
            "У вас пока что еще нет почт списке(",
            reply_markup=inline.add_emails_to_list_markup,
        )


# DEL EMAIL from EMAIL LIST
@commands_router.message(Command("del_emails"))
async def del_email(message: Message, state: FSMContext):
    await message.answer(
        f"<b>Напишите почту(ы) которую вы хотите удалить из  списка:</b>"
    )
    await state.set_state(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)


# TODO: удаление почт
@commands_router.message(DeletionEmailStatesGroup.WAIT_FOR_DEL_EMAIL)
@inject
async def email_del(
    message: Message,
    state: FSMContext,
    email_service: Annotated[EmailService, Depends()],
) -> None:
    emails_to_del = message.text.replace(" ", "").split(",")
    user_id = message.from_user.id

    emails_to_del_list = [{"user_id": user_id, "to": email} for email in emails_to_del]

    try:
        await email_service.delete_emails(emails_to_del_list)
        await message.answer(
            "Отлично, ты успешно удалил почты!\n Чтобы посмотреть актуальный список почт"
            " - воспользуйтесь \n/email_list"
        )

    except Exception:
        await message.answer(
            "Упс... Что-то пошло не так. Возможно такой почты не существует в вашем списке или произошла ошибка"
        )

    await state.clear()


@commands_router.message(Command("audio_list"))
@inject
async def get_audio_list_call(
    message: Message, audio_service: Annotated[AudioService, Depends()], bot: Bot
) -> None:
    user_id = message.from_user.id
    audio_list = await audio_service.get_audio_list(user_id)
    print(audio_list)

    if audio_list:
        chunks = [audio_list[i : i + 10] for i in range(0, len(audio_list), 10)]
        await message.answer("Вот ваш список аудио:")

        for audio_chunk in chunks:
            media_group = MediaGroupBuilder()
            # добавление аудио в builder
            [media_group.add_audio(media=audio) for audio in audio_chunk]
            await bot.send_media_group(user_id, media_group.build())

        await message.answer(
            "Можете выбрать действие ниже",
            reply_markup=inline.choose_audio_actions_kb_markup,
        )

    else:
        await message.answer(
            "У вас нет аудио в списке(", reply_markup=inline.add_audio_kb_markup
        )


@commands_router.message(SelfMailingStatesGroup.WAIT_FOR_EMAILS)
async def get_email_to_mail(message: Message, state: FSMContext):
    await state.update_data(email=message.text.replace(' ', '').replace(',', '\n'))
    await message.answer("Отправьте аудио 🎵")
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_AUDIOS)
