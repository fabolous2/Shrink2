from typing import Annotated
from aiogram import Router,Bot,F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, ContentType
from app.services import UserService
from dishka.integrations.aiogram import inject, Depends

from app.bot.keyboard import inline
from app.models.user import UserSubscription
from app.services.settings_service import SettingsService
from app.services.mailing_service import MailingService
from app.services.email_service import EmailService
from app.services.audio_service import AudioService

router=Router()

premium_one_month = LabeledPrice(label='Subscribe', amount=750)
premium_three_months = LabeledPrice(label='Subscribe', amount=1500)
premium_six_months = LabeledPrice(label='Subscribe', amount=2700)

basic_one_month = LabeledPrice(label='Subscribe', amount=400)
basic_three_months = LabeledPrice(label='Subscribe', amount=1000)
basic_six_months = LabeledPrice(label='Subscribe', amount=1800)


@router.callback_query(F.data == "premium_1_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на месяц',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR',
        prices=[premium_one_month],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    
@router.callback_query(F.data == "premium_3_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 3 месяца',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR', 
        prices=[premium_three_months],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    

@router.callback_query(F.data == "premium_6_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 6 месяцев',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR',
        prices=[premium_six_months],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    
@router.callback_query(F.data == "basic_1_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на месяц',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR',
        prices=[basic_one_month],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    

@router.callback_query(F.data == "basic_3_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 3 месяца',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR',
        prices=[basic_three_months],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    

@router.callback_query(F.data == "basic_6_sub")
async def order(query: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 6 месяцев',
        title='Monthly Subscription',
        payload='Payment through a bot',
        currency='XTR',
        prices=[basic_six_months],
        start_parameter='pay',
        provider_data=None,
        need_name=False,
        need_email=False,
        need_phone_number=False,
        need_shipping_address=False,
        send_email_to_provider=False,
        send_phone_number_to_provider=False,
        is_flexible=False,
        disable_notification=False,
        protect_content=True,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )
    
    
@router.pre_checkout_query(lambda query: True)
@inject
async def pre_checkout(
    pre_checkout: PreCheckoutQuery, bot: Bot,
    user_service: Annotated[UserService, Depends()], 
    settings_service: Annotated[SettingsService, Depends()], 
    mailing_service: Annotated[MailingService, Depends()], 
    email_service: Annotated[EmailService, Depends()],
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)
    total_amount = pre_checkout.total_amount
    user_id = pre_checkout.from_user.id

    if total_amount in [750, 1500, 2700]:
        await user_service.update_user(
            user_id=user_id,
            subscription=UserSubscription.PREMIUM, 
            email_limit = float('inf'), 
            audio_limit = float('inf')
        )       
        unavailable_list = await email_service.get_user_emails(user_id, available_is = 0)
        
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

    if total_amount == 750 or total_amount == 400:
        await user_service.update_user(user_id=user_id, sub_duration=30)
    elif total_amount == 1500 or total_amount == 1000:
        await user_service.update_user(user_id=user_id, sub_duration=90)
    else:
        await user_service.update_user(user_id=user_id, sub_duration=180)
    await mailing_service.update_sub_duration(user_id=user_id, bot=bot)
    await mailing_service.update_email_limit_to_send_for_extra(user_id=user_id, bot=bot)
        

#УСПЕШНАЯ ОПЛАТА
@router.message(F.data == ContentType.SUCCESSFUL_PAYMENT)
@inject
async def successful_payment(message: Message):
    payment_info = message.successful_payment.to_python()
    print('payment_info', payment_info)
    for k, v in payment_info.items():
        print(f"{k} = {v}")
    total_amount = message.successful_payment.total_amount // 100
    await message.answer(f"Платеж на сумму {total_amount} {message.successful_payment.currency} прошел успешно!!!")
