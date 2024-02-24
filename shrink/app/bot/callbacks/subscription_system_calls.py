from typing import Annotated

from dishka.integrations.aiogram import inject, Depends

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.models import UserSubscription
from app.services import UserService
from app.bot.utils import (
    get_basic_sub_info,
    get_without_sub_info,
    get_premium_sub_info,
    get_basic_subscription_price,
    get_premium_subscription_price
    )
from app.bot.keyboard import inline
from app.bot.states import SubscriptionActionsStatesGroup as SubscriptionStates

router = Router(name=__name__)


#! SUBSCRIPTION System
@router.callback_query(F.data == "subscription")
@inject
async def subscribes_call(query: CallbackQuery, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    email_and_password_filled = await user_service.user_email_and_password_is_set(user_id)
    subscription = await user_service.user_subscription(user_id)
    
    if not email_and_password_filled:
        return await query.message.edit_text('Сначала зарегистрируйтесь! 🧿',
                                             reply_markup=inline.profile_inline_kb_markup)
        
    if subscription == 'basic':
        await query.message.edit_text(get_basic_sub_info(),
                                      reply_markup=inline.cancel_subscription_kb_markup)
    
    elif subscription == 'premium':
            await query.message.edit_text(get_premium_sub_info,
                                          reply_markup=inline.cancel_subscription_kb_markup)
            
    else:
        await query.message.edit_text(get_without_sub_info(),
                                reply_markup=inline.subscription_menu_kb_markup)
        
        
@router.callback_query(F.data == 'back_to_subscriptions_choice')
@inject
async def choose_system_back_call(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscription = await user_service.user_subscription(user_id)

    if subscription == 'not_subscribed':
        await query.message.edit_text("Для начала выберите подписку", reply_markup=inline.subscription_choice_markup)
        return await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    
    if subscription == 'premium':
            await query.message.edit_text("Для начала выберите подписку",
                                          reply_markup=inline.basic_subscription_markup)
            await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    
    else:
        await query.message.edit_text("Для начала выберите подписку",
                                      reply_markup=inline.premium_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
    

@router.callback_query(F.data == 'purchase_subscription')
@inject
async def choose_paysystem_call(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscription = await user_service.user_subscription(user_id)

    if subscription == 'not_subscribed':
        await query.message.answer("Для начала выберите подписку",
                                   reply_markup=inline.subscription_choice_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
        

    elif subscription == 'premium':
        await query.message.answer("Для начала выберите подписку",
                                   reply_markup=inline.basic_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
       

    else:
        await query.message.answer("Для начала выберите подписку",
                                   reply_markup=inline.premium_subscription_markup)
        await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
            

@router.callback_query(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
@inject
async def pre_sub_choice(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id

    if query.data == 'basic':
        await query.message.edit_text(get_basic_subscription_price(),
                                      reply_markup=inline.payment_system_choice)
        
        #TODO: это после успешной оплаты
        await user_service.update_user(
                user_id=user_id,
                subscription=UserSubscription.BASIC
        )
        await state.clear()

    elif query.data == 'premium':
        await query.message.edit_text(get_premium_subscription_price(),
                                      reply_markup=inline.payment_system_choice)
        
        #TODO: это после успешной оплаты
        await user_service.update_user(
                user_id=user_id,
                subscription=UserSubscription.PREMIUM
        )
        await state.clear()


#! Choose The System
@router.callback_query(F.data == "freekassa_call")
async def freekassa_call_handler(query: CallbackQuery) -> None:
    await query.message.answer("Выберите длительность подписки",
                                reply_markup=inline.freekassa_sub_duration_markup)


@router.callback_query(F.data == 'ukassa_call')
async def ukassa_call_handler(query: CallbackQuery) -> None:
    await query.message.answer("Выберите длительность подписки",
                                   reply_markup=inline.ukassa_sub_duration_markup)