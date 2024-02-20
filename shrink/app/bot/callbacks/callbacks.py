from typing import Annotated

from aiogram import Router,F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Chat
from aiogram.filters import ExceptionMessageFilter

from app.bot.utils import (
    get_quit_profile, 
    get_profile_content, 
    get_registration_info,
    get_how_the_bot_works, 
    get_reg_start_info, 
    get_without_sub_info, 
    get_basic_sub_info,
    get_premium_sub_info, 
    get_basic_subscription_price, 
    get_premium_subscription_price, 
    get_pre_quit_text,
    get_mailing_registration_required,
    get_wait_email_addresses_text
)
from app.bot.keyboard import inline
from app.services import UserService
from app.bot.states import RegistrationStatesGroup, AddAudiosStatesGroup, DelAudioStatesGroup, SelfMailingStatesGroup, SendingEmailSchecule, EmailQuantityStatesGroup, DescriptionStatesGroup

from dishka.integrations.aiogram import inject, Depends

router = Router()

#! Main Menu
@router.callback_query(F.data == "main_menu")
async def menu_call(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        "🔮Выберите действия по кнопкам ниже:",
        chat_id=event_chat.id,
        reply_markup=inline.main_menu,
        message_id=query.inline_message_id,
    )


#! Logout of Profile
@router.callback_query(F.data == "quit_profile")
async def quit_profile(query: CallbackQuery, event_chat: Chat, bot: Bot) -> None:
    await bot.edit_message_text(
        get_quit_profile(),
        chat_id=event_chat.id,
        disable_web_page_preview=True,
        message_id=query.inline_message_id,
        reply_markup=inline.quit_profile_kb_markup, 
    )

@router.callback_query(F.data == "pre_quit")
async def pre_quit_profile(query: CallbackQuery) -> None:
    await query.message.edit_text(get_pre_quit_text(),
                                  reply_markup=inline.log_out_for_sure_button)


@router.callback_query(F.data == "quit")
async def quit_profile(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    
    #TODO: Удаление пользователя с БД
    await update_get_email_from(user_id, "None")
    await update_get_pwd_from(user_id, None)
    await update_sub(user_id, "none")
    await query.message.edit_text(text='''Вы успешно вышли из аккаунта! 🪫
Желаете создать новый?''', reply_markup=inline.profile_repeat_registration_kb_markup)


#! How The Bot Works
@router.callback_query(F.data == "how_work")
async def how_work_call(query:CallbackQuery) -> None:
    await query.message.edit_text(get_how_the_bot_works(), reply_markup=inline.back_to_main_menu_markup)


#! Getting User Profile Content
@router.callback_query(F.data == "profile")
async def get_user_profile_info(query: CallbackQuery, user_service: Annotated[UserService, Depends()]) -> None:
    user_id = query.from_user.id
    email_is_filled = await user_service.user_email_is_filled(user_id)

    if email_is_filled:
        await query.message.edit_text(get_profile_content(),
                                      reply_markup=inline.change_profile_markup,
                                      disable_web_page_preview=True)
        
    else:
        await query.message.edit_text(get_mailing_registration_required(),
                                      reply_markup=inline.profile_inline_kb_markup)


#!Попросили пока не трогать
#SUPPORT
# @router.callback_query(F.data=="support")
# async def support_call(query:CallbackQuery,state:FSMContext):
#     print(query.from_user.id)
#     await state.set_state(Sup.text)
#     await query.message.answer("""👀 Опиши проблему, которая у тебя возникла ⬇️
# <blockquote>Вопросы, предложения, сотрудничество тоже сюда!</blockquote>""",
#                                parse_mode='html')


# @router.callback_query(F.data=="sup_cancel")
# async def sup_cancel_call(query:Message | CallbackQuery,state:FSMContext):
#     state_data = await state.get_data()
#     await state.update_data(photo='None')
#     state_data["photo"] = 'None'
#     formatted_text = []
#     [
#         formatted_text.append(f'{value}')
#         for value in state_data.values()
#     ]
#     pattern=dict(text="<b>Подтвердите свою жалобу, она будет отправлена на обработку!</b>\n"
#                                    f"<blockquote>{state_data["text"]}</blockquote>",reply_markup=inline_builder(
#             ["✅ Подтвердить","🗑️ Отмена"],
#             ["agree_sup","fully_sup_cancel"]
#         ))

#     if isinstance(query,CallbackQuery):
#         await query.message.delete()
#         await query.message.answer(**pattern)

#     await state.set_state(Sup.send)


# @router.callback_query(F.data == "fully_sup_cancel")
# async def fully_sup_cancel(query: CallbackQuery):
#     global user_id
#     user_id = query.from_user.id
#     await query.message.delete()
#     await query.message.answer("🪬 Ваша жалоба успешно отменена!")



#! Cancel
@router.callback_query(F.data == "cancel")
async def cancel_call(query: CallbackQuery) -> None:
    await query.message.delete()


#! Auto-Mailing call
@router.callback_query(F.data == "auto_mailing")
async def auto_mailing_call(query:CallbackQuery) -> None:
    await query.message.edit_text("📮 Выберите действия по кнопкам ниже:", reply_markup=inline.choose_auto_mailing_actions_markup)


#! Auto-Mailing Settings
@router.callback_query(F.data == "settings")
async def settings_call(query: CallbackQuery) -> None:
    info = await get_email_info(user_id=query.from_user.id)

    await query.message.edit_text("Выберите,что вы хотите изменить в письме\n"
                                  "<b>Сейчас ваше письмо выглядит так:</b>\n\n"
                                  f"•Заголовок: <u>{info[0]}</u>\n"
                                  f"•Описание: <u>{info[1]}</u>\n"
                                  f"•Ежедневное время отправки: <u>{info[2]}</u>\n"
                                  f"•Кол-во аудио в письме за раз: <u>{info[3]}</u>", reply_markup=inline.settings_choice_markup)


@router.callback_query(F.data == "quantity")
async def quantity_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Напиши число от 1 до 10 аудио в письме(рекомендуется 2)")
    await state.set_state(EmailQuantityStatesGroup.WAIT_FOR_QUANTITY)


@router.callback_query(F.data == "description")
async def desc_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Напишите заголовок/тему к вашим будущим письмам")
    await state.set_state()


@router.callback_query(F.data == "mail_time")
async def mail_time_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Отправьте время в формате: (час):(минута) ")
    await state.set_state(SendingEmailSchecule.WAIT_FOR_TIME)


#! Self-Mailing
@router.callback_query(F.data == "self_mailing")
async def self_mailing_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_wait_email_addresses_text())
    await state.set_state(SelfMailingStatesGroup.WAIT_FOR_EMAILS)


#! Audio-list Actions
@router.callback_query(F.data == "add_audio")
async def add_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Отправьте аудио 🎵")
    await state.set_state(AddAudiosStatesGroup.WAIT_FOR_AUDIOS)


@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer("Отправьте боту аудио, которое хотите удалить")
    await state.set_state(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL)
