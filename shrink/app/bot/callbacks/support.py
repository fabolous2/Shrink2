import aiogram
from aiogram import F, Bot, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType, Chat

from app.bot.utils.bot_answer_text import (
    get_support_screen,
    get_user_complaint_content,
    get_successfull_complaint_cancel,
    get_successful_complaint_send,
    get_new_user_complaint_text,
    get_wrong_user_id
)
from app.bot.states import SupportStatesGroup
from app.bot.keyboard import inline
from app.main.config import ADMIN_ID

admin_user_id = ADMIN_ID
router = Router(name=__name__)


@router.message(
    StateFilter(SupportStatesGroup.WAIT_FOR_REPORT), F.content_type == ContentType.TEXT
)
async def get_screenshot(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await state.set_state(SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL)

    await message.answer(
        get_support_screen(),
        reply_markup=inline.complaint_sending_without_screen_markup,
    )


@router.callback_query(F.data == "send_complaint_without_screen")
async def sup_cancel_call(query: CallbackQuery, event_chat: Chat, bot: Bot, state: FSMContext) -> None:
    await state.update_data(photo="None")
    state_data = await state.get_data()
    await bot.delete_message(
        chat_id=event_chat.id,
        message_id=query.message.message_id,
    )

    await query.message.answer(
        text=get_user_complaint_content(state_data["text"]),
        reply_markup=inline.complaint_decision_markup,
    )

    await state.set_state(SupportStatesGroup.SENDING)


@router.message(
    SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL, F.content_type == ContentType.PHOTO
)
async def form_photo(message: Message, state: FSMContext) -> None:
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    state_data = await state.get_data()

    await message.answer_photo(
        photo=photo_file_id,
        caption=get_user_complaint_content(state_data["text"]),
        reply_markup=inline.complaint_decision_markup,
    )

    await state.set_state(SupportStatesGroup.SENDING)


@router.message(
    SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL, ~F.content_type == ContentType.PHOTO
)
async def failed_photo(message: Message) -> None:
    await message.answer("❗️Неверный формат❗️")


@router.callback_query(F.data == "cancel_complaint")
async def fully_sup_cancel(query: CallbackQuery) -> None:
    global user_id
    user_id = query.from_user.id
    await query.message.delete()
    await query.message.answer(get_successfull_complaint_cancel())


@router.callback_query(
    SupportStatesGroup.SENDING, F.data.in_(["cancel_complaint", "confirm_complaint"])
)
async def checkout_sup(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    global user_id
    user_id = query.from_user.id

    state_data = await state.get_data()
    await state.update_data(
        user_id=query.from_user.id,
        complaint_text=state_data["text"],
        photo=state_data,
    )
    
    if state_data["photo"] != "None":
        print(user_id, admin_user_id)
        await bot.forward_message(chat_id=admin_user_id,
                                  from_chat_id=user_id,
                                  message_id=query.message.message_id)
        
        await bot.send_message(
            admin_user_id,
            get_new_user_complaint_text(
                query.from_user.username, query.from_user.id
            ),
        )
        await query.message.delete()
        await bot.send_message(
            query.from_user.id,
            get_successful_complaint_send(),
            disable_web_page_preview=True,
        )

    else:
        print(admin_user_id, user_id)
        await bot.forward_message(
            chat_id=admin_user_id,
            from_chat_id=user_id,
            message_id=query.message.message_id - 2,
        )
        await bot.send_message(
            admin_user_id,
            get_new_user_complaint_text(
                query.from_user.username, query.from_user.id
            ),
        )

        await bot.send_message(
            query.from_user.id,
            get_successful_complaint_send(),
            disable_web_page_preview=True,
        )


@router.message(lambda message: message.from_user.id == 6644596826)
async def sup_check_admin(message: Message, bot: Bot) -> None:
    main_answer = "📮 Пришел ответ на ваше письмо!\n"
    if message.reply_to_message:
        answer_text = message.text[10:]
        user_chat_id = message.text[0:10]

        if message.reply_to_message.caption:
            caption_text = message.reply_to_message.caption[60:]
            blockquote_text = f"<blockquote>{caption_text}</blockquote>\n"
            user_photo = message.reply_to_message.photo[-1].file_id

            try:
                await bot.send_photo(
                    chat_id=user_chat_id,
                    photo=user_photo,
                    caption=main_answer + blockquote_text + "Ответ: " + answer_text,
                )
                await bot.send_message(admin_user_id, "Ответ отправлен пользователю")

            except aiogram.exceptions.TelegramBadRequest:
                await bot.send_message(
                    admin_user_id,
                    get_wrong_user_id(),
                )

        else:
            print(user_chat_id)
            caption_text = message.reply_to_message.text
            blockquote_text = f"<blockquote>{caption_text}</blockquote>\n"
            try:
                await bot.send_message(
                    chat_id=user_chat_id,
                    text=main_answer + blockquote_text + "Ответ: " + answer_text,
                )
                await bot.send_message(admin_user_id, "Ответ отправлен пользователю!")

            except aiogram.exceptions.TelegramBadRequest:
                await bot.send_message(
                    admin_user_id,
                    get_wrong_user_id(),
                )
