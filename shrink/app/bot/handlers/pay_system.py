from aiogram import Router,Bot,F
from aiogram.types import Message,LabeledPrice,PreCheckoutQuery,CallbackQuery,ContentType
from keyboards.builder import inline_builder
router=Router()

#ЮKassa PAYMENT
payment_token='381764678:TEST:77033'
one_month = LabeledPrice(label='Subscribe', amount=99900)
three_months = LabeledPrice(label='Subscribe', amount=249900)
six_months = LabeledPrice(label='Subscribe', amount=399900)

@router.callback_query(F.data=="u_1_sub")
async def order(query:CallbackQuery,bot:Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на месяц',
        title='Monthly Subscription',
        payload='Payment through a bot',
        provider_token=payment_token,
        currency='rub',
        prices=[one_month],
        max_tip_amount=5000,
        suggested_tip_amounts=[500,1000,2000,3000],
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

@router.callback_query(F.data=="u_3_sub")
async def order(query:CallbackQuery,bot:Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 3 месяца',
        title='3 Months Subscription',
        payload='Payment through a bot',
        provider_token=payment_token,
        currency='rub',
        prices=[three_months],
        max_tip_amount=5000,
        suggested_tip_amounts=[500,1000,2000,3000],
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

@router.callback_query(F.data=="u_6_sub")
async def order(query:CallbackQuery,bot:Bot):
    await bot.send_invoice(
        chat_id=query.from_user.id,
        description='Подписка на 6 месяцев',
        title='6 Months Subscription',
        payload='Payment through a bot',
        provider_token=payment_token,
        currency='rub',
        prices=[six_months],
        max_tip_amount=5000,
        suggested_tip_amounts=[500,1000,2000,3000],
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


#PRE_CHECKOUT
@router.pre_checkout_query(lambda query:True)
async def pre_checkout(pre_checkout:PreCheckoutQuery,bot:Bot):
    await bot.answer_pre_checkout_query(pre_checkout.id,ok=True)


#УСПЕШНАЯ ОПЛАТА
@router.message(F.data==ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await message.answer(f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


#FREEKASSA PAYMENT
@router.callback_query(F.data.in_(["free_1_sub","free_3_sub","free_6_sub"]))
async def freekassa_purchase(query:CallbackQuery):
    if query.data=="free_1_sub":
        await query.message.answer("Сумма к оплате: 999 RUB\n\n"
                            " Чтобы оплатить 🎒 Подписку необходимо оплатить счет по ссылке ниже\n"
                            "*ссылка FreeKassa*\n\n"
                            "❗Важно❗\n"
                            "После оплаты Подписка будет выдана автоматически\n\n"
                            "Для отмены нажми кнопку «❌Отменить»",reply_markup=inline_builder(
            ["❌Отменить"],
            ["cancel"]
        ))
    elif query.data=="free_3_sub":
        await query.message.answer("Сумма к оплате: 2499 RUB\n\n"
                            " Чтобы оплатить 🎒 Подписку необходимо оплатить счет по ссылке ниже\n"
                            "*ссылка FreeKassa*\n\n"
                            "❗Важно❗\n"
                            "После оплаты Подписка будет выдана автоматически\n\n"
                            "Для отмены нажми кнопку «❌Отменить»",reply_markup=inline_builder(
            ["❌Отменить"],
            ["cancel"]
        ))
    if query.data=="free_6_sub":
        await query.message.answer("Сумма к оплате: 3999 RUB\n\n"
                            " Чтобы оплатить 🎒 Подписку необходимо оплатить счет по ссылке ниже\n"
                            "*ссылка FreeKassa*\n\n"
                            "❗Важно❗\n"
                            "После оплаты Подписка будет выдана автоматически\n\n"
                            "Для отмены нажми кнопку «❌Отменить»",reply_markup=inline_builder(
            ["❌Отменить"],
            ["cancel"]
        ))