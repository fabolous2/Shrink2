from typing import Annotated

from dishka.integrations.aiogram import inject, Depends

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services import UserServices
from app.bot.utils import get_basic_sub_info, get_without_sub_info, get_premium_sub_info

router = Router()


#! SUBSCRIPTIONs System
@router.callback_query(F.data == "subscribes")
async def subscribes_call(query: CallbackQuery, user_service: Annotated[UserServices, Depends()]) -> None:
    user_id = query.from_user.id
    email_is_filled = await user_service.user_email_is_filled(user_id)
    
    if not email_is_filled:
        await query.message.edit_text('Сначала зарегистрируйтесь! 🧿',
                                      reply_markup=inline.profile)
    else:
        if await database.get_premium(user_id) == 'none':
            await query.message.edit_text(get_without_sub_info(),
                                          reply_markup=inline.sub_menu)

        elif await database.get_premium(user_id) == 'basic':
            await query.message.edit_text(get_basic_sub_info(),
                                          reply_markup=inline.sub_cancel)

        else:
            await query.message.edit_text(get_premium_sub_info,
                                          reply_markup=inline.sub_cancel)


@router.callback_query(F.data.in_(["paysystem_purchase_sub", "back_sub"]))
async def choose_system_call(query: CallbackQuery, state: FSMContext) -> None:
    user_id = query.from_user.id

    if await database.get_premium(user_id) == 'none':
        if query.data == 'paysystem_purchase_sub':
            await query.message.answer("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥇premium", "🥈basic"],
                ["premium", "basic"]
            ))
            await state.set_state(Sub.pre_sub_choice)
        else:
            await query.message.edit_text("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥇premium", "🥈basic"],
                ["premium", "basic"]
            ))
            await state.set_state(Sub.pre_sub_choice)

    elif await database.get_premium(user_id) == 'basic':
        if query.data == 'paysystem_purchase_sub':
            await query.message.answer("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥇premium"],
                ["premium"]
            ))
            await state.set_state(Sub.pre_sub_choice)
        else:
            await query.message.edit_text("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥇premium"],
                ["premium"]
            ))
            await state.set_state(Sub.pre_sub_choice)
    else:
        if query.data == 'paysystem_purchase_sub':
            await query.message.answer("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥈basic"],
                ["basic"]
            ))
            await state.set_state(Sub.pre_sub_choice)
        else:
            await query.message.edit_text("Для начала выберите подписку", reply_markup=inline_builder(
                ["🥈basic"],
                ["basic"]
            ))
            await state.set_state(Sub.pre_sub_choice)


@router.callback_query(Sub.pre_sub_choice)
async def pre_sub_choice(query: CallbackQuery, state: FSMContext) -> None:
    user_id = query.from_user.id

    if query.data == 'basic':
        await query.message.edit_text(get_basic_subscription_price(),
                                   reply_markup=inline_builder(
                                       ["ЮKassa", "FreeKassa", "⬅ Назад"],
                                       ["ukassa_call", "freekassa_call", "back_sub"],
                                       [2, 1]
                                   ))
        await database.update_pre_sub(user_id, 'basic')
        await state.clear()

    elif query.data == 'premium':
        await query.message.edit_text(get_premium_subscription_price,
                                       reply_markup=inline_builder(
                                       ["ЮKassa", "FreeKassa", "⬅ Назад"],
                                       ["ukassa_call", "freekassa_call", "back_sub"],
                                       [2, 1]
                                   ))
        await database.update_pre_sub(user_id, 'premium')
        await state.clear()


@router.callback_query(F.data.in_(["ukassa_call", "freekassa_call"]))
async def payment_system_call(query: CallbackQuery) -> None:
    if query.data == "ukassa_call":
        await query.message.answer("Выберите длительность подписки", reply_markup=inline_builder(
            ["1 month subscription", "3 months subscription", "6 months subscription"],
            ["u_1_sub", "u_3_sub", "u_6_sub"],
            [1, 1, 1]
        ))

    if query.data == "freekassa_call":
        await query.message.answer("Выберите длительность подписки", reply_markup=inline_builder(
            ["1 month subscription", "3 months subscription", "6 months subscription"],
            ["free_1_sub", "free_3_sub", "free_6_sub"],
            [1, 1, 1]
        ))