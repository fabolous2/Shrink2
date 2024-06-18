from typing import Annotated

from dishka.integrations.aiogram import inject, Depends

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.models import UserSubscription
from app.services import UserService
from app.bot.utils.bot_answer_text import (
    get_basic_sub_info,
    get_change_from_basic,
    get_change_from_premium,
    get_mailing_registration_required,
    get_without_sub_info,
    get_premium_sub_info,
    get_basic_subscription_price,
    get_premium_subscription_price, 
    get_sub_choice
    )
from app.bot.keyboard import inline
from app.bot.states import SubscriptionActionsStatesGroup as SubscriptionStates
from app.services.email_service import EmailService
from app.services.audio_service import AudioService

router = Router(name=__name__)


#! SUBSCRIPTION System
@router.callback_query(F.data == "subscription")
@inject
async def subscribes_call(query: CallbackQuery, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    is_registered = await user_service.user_is_registered(user_id)
    subscription = await user_service.user_subscription(user_id)
    sub_duration = await user_service.get_sub_duration(user_id)
    
    if not is_registered:
        return await query.message.edit_text(get_mailing_registration_required(), reply_markup=inline.profile_inline_kb_markup)   
    if subscription == 'basic':
        await query.message.edit_text(get_basic_sub_info(sub_duration), reply_markup=inline.cancel_subscription_kb_markup)
    elif subscription == 'premium':
        await query.message.edit_text(get_premium_sub_info(sub_duration), reply_markup=inline.cancel_subscription_kb_markup)   
    else:
        await query.message.edit_text(get_without_sub_info(), reply_markup=inline.subscription_menu_kb_markup)
        
        
@router.callback_query(F.data == 'back_to_subscriptions_choice')
@inject
async def choose_system_back_call(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscription = await user_service.user_subscription(user_id)

    if subscription == 'free':
        await query.message.edit_text(get_sub_choice(), reply_markup=inline.subscription_choice_markup)
        return await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    if subscription == 'premium':
            await query.message.edit_text(get_sub_choice(), reply_markup=inline.basic_subscription_markup)
            await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    else:
        await query.message.edit_text(get_sub_choice(), reply_markup=inline.premium_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    

@router.callback_query(F.data == 'purchase_subscription')
@inject
async def choose_paysystem_call(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscription = await user_service.user_subscription(user_id)

    if subscription == 'free':
        await query.message.edit_text(user_id=user_id, text=get_sub_choice(), reply_markup=inline.subscription_choice_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    elif subscription == 'premium':
        await query.message.answer(get_sub_choice(), reply_markup=inline.basic_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE) 
    else:
        await query.message.answer(get_sub_choice(), reply_markup=inline.premium_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
        
        
@router.callback_query(F.data == 'change_subscription')
@inject
async def change_subscription(query: CallbackQuery, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscription = await user_service.user_subscription(user_id)
    user = await user_service.get_user(user_id=user_id)

    sub_duration_for_basic = int(user.sub_duration * 1.6)
    sub_duration_for_premium = int(user.sub_duration * 0.6) 
    
    if subscription == 'premium':
        await query.message.edit_text(text=get_change_from_basic(sub_duration_for_basic), reply_markup=inline.change_sub_to_prem_kb_markup)   
    elif subscription == 'basic':
        await query.message.edit_text(text=get_change_from_premium(sub_duration_for_premium), reply_markup=inline.change_sub_to_basic_kb_markup)
            
            
@router.callback_query(F.data == 'change_sub_to_basic')
@inject
async def final_change_to_basic(
    query: CallbackQuery,
    user_service: Annotated[UserService, Depends()], 
    email_service: Annotated[EmailService, Depends()], 
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    user_id = query.from_user.id
    await query.message.edit_text("Ваша подписка успешно изменена на basic")
    sub_duration = int(await user_service.get_sub_duration(user_id) * 1.6)
    print(sub_duration)
    
    await user_service.update_user(
        user_id=query.from_user.id,
        subscription=UserSubscription.BASIC, 
        email_limit = 1800, 
        audio_limit = 200
    ) 
    await user_service.update_user(user_id=user_id, sub_duration = sub_duration)
    
    available_list = await email_service.get_user_emails(user_id, available_is = 1)
    if len(available_list) > 1800:
        list_to_del = available_list[:len(available_list)-1800]
        for email in list_to_del:
            await email_service.update_available_is(user_id, email, available_is=0)
            
    available_audio_list = await audio_service.get_audio_list(user_id, available_is=1)
    if available_audio_list:
        if len(available_audio_list) > 200:
            available_audio_list = available_audio_list[:len(available_audio_list)-200]
            audio_dicts = [
                {
                    'id': audio.id,
                    'file_id': audio.file_id,
                    'name': audio.name,
                    'size': audio.size,
                    'user_id': audio.user_id,
                    'audio_index': audio.audio_index,
                    'is_extra': audio.is_extra,
                    'available_is_for_audio': 0 
                } for audio in available_audio_list
            ]
            await audio_service.update_audio_list(audio_dicts)    


@router.callback_query(F.data == 'change_sub_to_prem')
@inject
async def final_change_to_prem(
    query: CallbackQuery,
    user_service: Annotated[UserService, Depends()],
    email_service: Annotated[EmailService, Depends()], 
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    user_id = query.from_user.id
    sub_duration = int(await user_service.get_sub_duration(user_id) * 0.6)
    
    await user_service.update_user(
        user_id=user_id,
        subscription=UserSubscription.PREMIUM, 
        email_limit=float('inf'), 
        audio_limit=float('inf')
    ) 
    await user_service.update_user(user_id=user_id, sub_duration = sub_duration)
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
        
    await query.message.edit_text("Ваша подписка успешно изменена на premium")
    

@router.callback_query(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
@inject
async def pre_sub_choice(query: CallbackQuery) -> None:
    if query.data == 'basic':
        await query.message.edit_text(get_basic_subscription_price(), reply_markup=inline.basic_sub_duration_markup)
    elif query.data == 'premium':
        await query.message.edit_text(get_premium_subscription_price(), reply_markup=inline.premium_sub_duration_markup)
