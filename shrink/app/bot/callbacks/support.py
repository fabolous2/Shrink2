import aiogram
from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, ContentType

from app.bot.utils import (get_support_answer,
                           get_support_screen,
                           get_user_complaint_content,
                           get_successfull_complaint_cancel,
                           get_successful_complaint_send,
                           get_new_user_complaint_text
                           )
from app.bot.states import SupportStatesGroup
from app.bot.keyboard import inline
from app.main.config import ADMIN_ID

admin_user_id = 0
router = Router(name=__name__)


@router.message(StateFilter(SupportStatesGroup.WAIT_FOR_REPORT), F.content_type == ContentType.TEXT)
async def get_screenshot(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await state.set_state(SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL)
    await message.answer(get_support_screen(), reply_markup=inline.complaint_sending_without_screen)


@router.callback_query(F.data == "send_complaint_without_screen")
async def sup_cancel_call(query: Message | CallbackQuery, state: FSMContext) -> None:
    state_data = await state.get_data()
    await state.update_data(photo='None')
    state_data["photo"] = 'None'
    formatted_text = []
    [
        formatted_text.append(f'{value}')
        for value in state_data.values()
    ]
    pattern = dict(get_user_complaint_content(), reply_markup=inline.complaint_decision_markup)

    if isinstance(query,CallbackQuery):
        await query.message.delete()
        await query.message.answer(**pattern)

    await state.set_state(SupportStatesGroup.SENDING)


@router.message(SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL, F.content_type == ContentType.PHOTO)
async def form_photo(message: Message, state: FSMContext) -> None:
    photo_file_id = message.photo[-1].file_id
    state_data = await state.get_data()
    await state.update_data(photo=photo_file_id)
    state_data["photo"] = photo_file_id 
    formatted_text = "\n".join([f"<b>{key}</b>: {value}" for key, value in state_data.items()])

    await message.answer_photo(photo_file_id,
                               get_user_complaint_content(state_data),
                               reply_markup=inline.complaint_decision_markup)
    await state.set_state(SupportStatesGroup.SENDING)


@router.message(SupportStatesGroup.WAIT_FOR_SCREEN_OPTIONAL, ~F.content_type == ContentType.PHOTO)
async def failed_photo(message: Message) -> None:
    await message.answer("❗️Неверный формат❗️")


@router.callback_query(F.data == "cancel_complaint")
async def fully_sup_cancel(query: CallbackQuery) -> None:
    global user_id
    user_id = query.from_user.id
    await query.message.delete()
    await query.message.answer(get_successfull_complaint_cancel())


@router.callback_query(SupportStatesGroup.SENDING, F.data.in_(["cancel_complaint", "confirm_complaint"]))
async def checkout_sup(query: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    global user_id
    user_id = query.from_user.id

    if query.data == "fully_sup_cancel":
        await query.message.delete()
        await query.message.answer(get_successfull_complaint_cancel())

    elif query.data == "confirm_complaint":
        state_data = await state.get_data()
        await state.update_data(
            user_id=query.from_user.id,
            complaint_text=state_data["text"],
            photo=state_data["photo"]
        )

        if state_data['photo'] != 'None':
            await bot.forward_message(admin_user_id,
                                      user_id,
                                      query.message.message_id)
            await bot.send_message(admin_user_id,
                                   get_new_user_complaint_text(query.from_user.username, query.from_user.id))
            await query.message.delete()
            await bot.send_message(query.from_user.id,
                                   get_successful_complaint_send(), 
                                   disable_web_page_preview=True)

        else:
            await bot.forward_message(chat_id=admin_user_id,
                                      from_chat_id=user_id,
                                      message_id=query.message.message_id - 2)
            await bot.send_message(admin_user_id,
                                   get_new_user_complaint_text(query.from_user.username, query.from_user.id))

            await bot.send_message(query.from_user.id, get_successful_complaint_send(),
                                   disable_web_page_preview=True)


@router.message(F.chat.id == ADMIN_ID)
async def sup_check_admin(message: Message, bot: Bot) -> None:
    main_answer = '📮 Пришел ответ на ваше письмо!\n'
    if message.reply_to_message:
        answer_text = message.text[10:]
        user_chat_id = message.text[0:10]

        if message.reply_to_message.caption:
            caption_text = message.reply_to_message.caption[60:]
            blockquote_text = f"<blockquote>{caption_text}</blockquote>\n"
            user_photo = message.reply_to_message.photo[-1].file_id

            try:
                await bot.send_photo(chat_id=user_chat_id,
                                     photo=user_photo,
                                     caption=main_answer + blockquote_text + 'Ответ: ' + answer_text)
                await bot.send_message(admin_user_id, "Ответ отправлен пользователю")

            except aiogram.exceptions.TelegramBadRequest:
                await bot.send_message(admin_user_id, f"Что-то пошло не так.\n"
                                                      f"Возможно неправильно введен user_id")

        else:
            caption_text = message.reply_to_message.text
            blockquote_text = f"<blockquote>{caption_text}</blockquote>\n"
            try:
                await bot.send_message(chat_id=user_chat_id,
                                       text=main_answer + blockquote_text + 'Ответ: ' + answer_text)
                await bot.send_message(admin_user_id, "Ответ отправлен пользователю")

            except aiogram.exceptions.TelegramBadRequest:
                await bot.send_message(admin_user_id, f"Что-то пошло не так.\n"
                                                      f"Возможно неправильно введен user_id")

