from typing import Annotated

from dishka.integrations.aiogram import inject, Depends

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services import UserService
from app.bot.utils import get_basic_sub_info, get_without_sub_info, get_premium_sub_info, get_basic_subscription_price, get_premium_subscription_price
from app.bot.keyboard import inline
from app.bot.states import SubscriptionActionsStatesGroup as SubscriptionStates

router = Router()


#! SUBSCRIPTION System
@router.callback_query(F.data == "subscribes")
@inject
async def subscribes_call(query: CallbackQuery, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    email_and_password_filled = await user_service.user_email_and_password_is_set(user_id)
    subscription = await user_service.user_subscription(user_id)
    
    if not email_and_password_filled:
        return await query.message.edit_text('Сначала зарегистрируйтесь! 🧿',
                                      reply_markup=inline.profile)
        
    if subscription == 'basic':
        await query.message.edit_text(get_basic_sub_info(),
                                        reply_markup=inline.sub_cancel)
    
    elif subscription == 'premium':
            await query.message.edit_text(get_premium_sub_info,
                                    reply_markup=inline.sub_cancel)
            
    else:
        await query.message.edit_text(get_without_sub_info(),
                                reply_markup=inline.sub_menu)
        
        

#! НА ДОРАБОТКЕ
@router.callback_query(F.data == 'back_to_subscriptions_choice')
@inject
async def choose_system_back_call(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    await query.message.edit_text("Для начала выберите подписку", reply_markup=inline.subscription_choice_markup)
    await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)


@router.callback_query(F.data == 'paysystem_purchase_sub')
@inject
async def choose_system_call(query: CallbackQuery, state: FSMContext, user_servise: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    subscriptions = await user_servise.user_subscription(user_id)

    if subscriptions == 'none':
        if query.data == 'paysystem_purchase_sub':
            await query.message.answer("Для начала выберите подписку", reply_markup=inline.subscription_choice_markup)
            await state.set_state(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
            

    # elif subscriptions == 'basic':

    #     if query.data == 'paysystem_purchase_sub':
    #         await query.message.answer("Для начала выберите подписку", reply_markup=inline_builder(
    #             ["🥇premium"],
    #             ["premium"]
    #         ))
    #         await state.set_state(Sub.pre_sub_choice)

    #     else:

    #             ["🥇premium"],
    #             ["premium"]
    #         ))
    #         await state.set_state(Sub.pre_sub_choice)

    # else:
    #     if query.data == 'paysystem_purchase_sub':
    #         await query.message.answer("Для начала выберите подписку", reply_markup=inline_builder(
    #             ["🥈basic"],
    #             ["basic"]
    #         ))
    #         await state.set_state(Sub.pre_sub_choice)

    #     else:
    #         await query.message.edit_text("Для начала выберите подписку", reply_markup=inline_builder(
    #             ["🥈basic"],
    #             ["basic"]
    #         ))
    #         await state.set_state(Sub.pre_sub_choice)


@router.callback_query(SubscriptionStates.WAIT_FOR_SUBSCRIPTION_TYPE)
@inject
async def pre_sub_choice(query: CallbackQuery, state: FSMContext, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id

    if query.data == 'basic':
        await query.message.edit_text(get_basic_subscription_price(),
                                   reply_markup=inline.payment_system_choice)
        await user_service.update_user(user_id, 'basic')
        await state.clear()

    elif query.data == 'premium':
        await query.message.edit_text(get_premium_subscription_price(),
                                       reply_markup=inline.payment_system_choice)
        await user_service.update_user(user_id, 'premium')
        await state.clear()


@router.callback_query(F.data.in_(["ukassa_call", "freekassa_call"]))
async def payment_system_call(query: CallbackQuery) -> None:
    if query.data == "ukassa_call":
        await query.message.answer("Выберите длительность подписки", reply_markup=inline.ukassa_sub_duration_markup)

    if query.data == "freekassa_call":
        await query.message.answer("Выберите длительность подписки", reply_markup=inline.freekassa_sub_duration_markup)