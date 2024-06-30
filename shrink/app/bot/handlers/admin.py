import re
from typing import Annotated

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, Chat
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from dishka.integrations.aiogram import inject, Depends

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.keyboard import inline, builder
from app.services import (
    UserService,
    EmailService,
    AudioService,
    SettingsService,
    MailingService,
)
from app.bot.filters import AdminProtect
from app.bot.states import SubscriptionIssuingSG
from app.models.user import UserSubscription


admin = Router(name=__name__)


class Newsletter(StatesGroup):
    message = State()
    photo = State()
    confirm = State()


@admin.message(AdminProtect(), Command('apanel'))
@admin.callback_query(AdminProtect(), F.data.in_(["menu", "menu_after_photo"]))
async def apanel(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await message.answer(
            "Возможные комманды:",
            reply_markup=inline.mailing_for_admin_markup
        )
    else:
        if message.data == "menu":
            await message.message.edit_text(
                "Возможные комманды:",
                reply_markup=inline.mailing_for_admin_markup
            )
        else:
            await message.message.answer(
                "Возможные комманды:",
                reply_markup=inline.mailing_for_admin_markup
            )


@admin.callback_query(AdminProtect(), F.data == "subscription_issuing")
async def subscription_issuing_handler(
    query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    event_chat: Chat
) -> None:
    await bot.send_message(
        chat_id=event_chat.id,
        text='🪪 Введите <code>user_id</code> или же <code>почту</code> пользователя, которому желаете выдать подписку.',
    )
    await state.set_state(SubscriptionIssuingSG.IDENTIFIER)


@admin.message(AdminProtect(), SubscriptionIssuingSG.IDENTIFIER)
@inject
async def choosing_subscription_type_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    event_chat: Chat,
    user_service: Annotated[UserService, Depends()],
) -> None:
    await bot.delete_message(chat_id=event_chat.id, message_id=message.message_id - 1)
    await state.clear()
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if message.text.replace(' ', '').isdigit():
        user_id = int(message.text)
        user = await user_service.get_user(user_id=user_id)

        if user:
            await state.update_data(user_id=user_id)
        else:
            await bot.send_message(
                chat_id=event_chat.id,
                text="😔 К сожалению, бот не сумел найти пользователя с теми данными, которые вы отправили.",
                reply_markup=inline.again_searching_markup,
            )
            await state.clear()
            return
    elif re.match(email_pattern, message.text):
        email = message.text.lower()
        user = await user_service.get_user(personal_email=email)

        if user:
            await state.update_data(user_id=user.user_id)
        else:
            await bot.send_message(
                chat_id=event_chat.id,
                text="😔 К сожалению, бот не сумел найти пользователя с теми данными, которые вы отправили.",
                reply_markup=inline.again_searching_markup,
            )
            await state.clear()
            return
    else:
        await bot.send_message(
            chat_id=event_chat.id,
            text="⛔ Вы ввели неправильные данные. Вы должны ввести либо <b>id</b> пользователя, либо его <b>почту</b>.",
            reply_markup=inline.again_searching_markup,
        )
        await state.clear()
        return
    
    await bot.send_message(
            chat_id=event_chat.id,
            text="🎫 Выберите тип подписки.",
            reply_markup=inline.subscription_types_markup,
        )
    await state.set_state(SubscriptionIssuingSG.TYPE)
    

@admin.callback_query(AdminProtect(), SubscriptionIssuingSG.TYPE, F.data.in_(['premium_type', 'basic_type']))
async def sub_duration_handler(
    query: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    event_chat: Chat,
) -> None:
    await query.message.delete()
    subscription_type = query.data[:-5]
   
    await state.update_data(subscription_type=subscription_type)
    await bot.send_message(
        chat_id=event_chat.id,
        text='⏳ Выберите продолжительность подписки пользователя.',
        reply_markup=inline.duration_markup,
    )
    await state.set_state(SubscriptionIssuingSG.DURATION)


@admin.callback_query(
    AdminProtect(),
    SubscriptionIssuingSG.DURATION,
    F.data.in_(['one_month_subscription', 'three_months_subscription', 'six_months_subscription'])
)
@inject
async def subscription_duration_handler(
    query: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    user_service: Annotated[UserService, Depends()],
    email_service: Annotated[EmailService, Depends()],
    audio_service: Annotated[AudioService, Depends()],
    settings_service: Annotated[SettingsService, Depends()],
    mailing_service: Annotated[MailingService, Depends()],
    scheduler: AsyncIOScheduler,
) -> None:
    await query.message.delete()
    state_data = await state.get_data()
    subscription_type = state_data['subscription_type']
    
    user_id = state_data['user_id']

    if subscription_type == 'premium':
        await user_service.update_user(
            user_id=user_id,
            subscription=UserSubscription.PREMIUM, 
            email_limit=float('inf'), 
            audio_limit=float('inf')
        )       
        unavailable_list = await email_service.get_user_emails(user_id, available_is=0)
        
        if unavailable_list:
            for email in unavailable_list:
                await email_service.update_available_is(user_id, email, available_is=1)
                
        unavailable_audio_list = await audio_service.get_audio_list(user_id, available_is=0)
        if unavailable_audio_list:
            audio_dicts = [
                {
                    'id': audio.id,
                    'file_id': audio.file_id,
                    'name': audio.name,
                    'size': audio.size,
                    'user_id': audio.user_id,
                    'audio_index': audio.audio_index,
                    'is_extra': audio.is_extra,
                    'available_is_for_audio': 1 
                } for audio in unavailable_audio_list
            ]
            await audio_service.update_audio_list(audio_dicts)
    else:
        await user_service.update_user(
            user_id=user_id,
            subscription=UserSubscription.BASIC, 
            email_limit=1800, 
            audio_limit=200
        ) 
        
        unavailable_list = await email_service.get_user_emails(user_id, available_is=0)
        old_list = await email_service.get_user_emails(user_id, available_is=1)
        
        if unavailable_list and old_list:
            combined_list = unavailable_list + old_list
        elif old_list:
            combined_list = old_list
        else:
            combined_list = unavailable_list

        if unavailable_list:
            if len(combined_list) > 1800:
                len_without_limit = 1800 - len(old_list)
                if len_without_limit > 0:
                    unavailable_list = unavailable_list[-len_without_limit:] 
                else:
                    unavailable_list = []
                combined_list = unavailable_list + old_list
            for email in combined_list:
                await email_service.update_available_is(user_id, email, available_is=1)
                
    unavailable_audio_list = await audio_service.get_audio_list(user_id, available_is=0)
    available_audio_list = await audio_service.get_audio_list(user_id, available_is=1)
    if available_audio_list:
        len_without_limit_for_audio = 200 - len(available_audio_list)
    else:
        len_without_limit_for_audio = 200

    if unavailable_audio_list:
        unavailable_audio_list = unavailable_audio_list[-len_without_limit_for_audio:]
        audio_dicts = [
                {
                    'id': audio.id,
                    'file_id': audio.file_id,
                    'name': audio.name,
                    'size': audio.size,
                    'user_id': audio.user_id,
                    'audio_index': audio.audio_index,
                    'is_extra': audio.is_extra,
                    'available_is_for_audio': 1 
                } for audio in unavailable_audio_list
            ]
        await audio_service.update_audio_list(audio_dicts)
       
    await settings_service.update_email_limit_to_send(user_id=user_id, count=450)
    await settings_service.update_settings(user_id, email_limit_to_send_for_extra=50)

    # duration
    if query.data == "one_month_subscription":
        await user_service.update_user(user_id=user_id, sub_duration=30)
    elif query.data == "three_months_subscription":
        await user_service.update_user(user_id=user_id, sub_duration=90)
    else:
        await user_service.update_user(user_id=user_id, sub_duration=180)

    # await mailing_service.update_sub_duration(user_id=user_id, bot=bot)
    sub = await user_service.get_sub_duration(user_id)
    if sub >= 0:
        scheduler.add_job(
        func=user_service.update_sub_duration,
        trigger="cron",
        hour=0,
        minute=0,
        kwargs={'user_id': user_id, 'bot': bot}
    )
    scheduler.add_job(
        func=user_service.update_email_limit_to_send_for_extra,
        trigger="cron",
        hour=0,
        minute=0,
        kwargs={'user_id': user_id, 'bot': bot}
        )
    scheduler.start()
    # await mailing_service.update_email_limit_to_send_for_extra(user_id=user_id, bot=bot)
    await query.message.answer("Вы успешно выдали пользователю подписку !")


# LETTERS
@admin.callback_query(AdminProtect(), F.data == 'newsletter')
async def newsletter(query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Newsletter.message)
    await query.message.answer("Введите сообщение, которое нужно разослать пользователям")


@admin.message(AdminProtect(), Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(Newsletter.photo)
    await message.answer("📷 Можете приложить скриншот (не обязательно)", reply_markup=builder.inline_builder(
        ["📮 Отправить сейчас"],
        ["sup_cancel_admin"],
        [1]
    ))


@admin.message(AdminProtect(), Newsletter.photo, F.photo)
async def newsletter_photo(message: Message, state: FSMContext):
    await message.delete()
    photo_file_id = message.photo[-1].file_id
    state_data = await state.get_data()
    await state.update_data(photo=photo_file_id)
    state_data["photo"] = photo_file_id
    await state.update_data(photo=state_data['photo'])
    await message.answer_photo(state_data['photo'],
                               f"{state_data['message']}\n<blockquote>Уверены что хотите разослать это сообщение?</blockquote>",
                               reply_markup=builder.inline_builder(
                                   ["✅ Разослать", "❌ Отмена"],
                                   ["confirm", "menu_after_photo"],
                                   [1]
                               ),
                               parse_mode="html")
    await state.set_state(Newsletter.confirm)


@admin.message(AdminProtect(), Newsletter.photo, ~F.photo)
async def failed_photo(message: Message):
    await message.answer("❗️Неверный формат❗️")


@admin.callback_query(AdminProtect(), F.data == 'sup_cancel_admin')
async def newsletter_sup_cancel(message: CallbackQuery | Message, state: FSMContext):
    state_data = await state.get_data()
    await state.update_data(message=state_data['message'],
                            photo='None')
    await message.message.answer(f"{state_data['message']}\n <blockquote>Уверены что хотите разослать это сообщение?</blockquote>",
                                 reply_markup=builder.inline_builder(
                                     ["✅ Разослать", "❌ Отмена"],
                                     ["confirm", "menu"],
                                     [1]
                                 ),
                                 parse_mode='html')
    await state.set_state(Newsletter.confirm)


@admin.callback_query(AdminProtect(), Newsletter.confirm, F.data == "confirm")
@inject
async def newsletter_confirm(query: CallbackQuery, state: FSMContext, bot: Bot,
                             user_service: Annotated[UserService, Depends()]):
    user_ids = await user_service.get_all_user_ids()
    print(user_ids)
    state_data = await state.get_data()
    await state.update_data(message=state_data['message'],
                            photo=state_data['photo'])

    if state_data["photo"] != "None":
        await query.message.answer("Подождите... Идет рассылка.")
        for user in user_ids:
            await bot.send_photo(chat_id=user,
                                 photo=state_data['photo'],
                                 caption=state_data['message'])
        await query.message.answer("Рассылка успешно завершена.")
    else:
        await query.message.answer("Подождите... Идет рассылка.")
        for user in user_ids:
            await bot.send_message(user,
                                   state_data['message'])
        await query.message.answer("Рассылка успешно завершена.")
    await state.clear()
