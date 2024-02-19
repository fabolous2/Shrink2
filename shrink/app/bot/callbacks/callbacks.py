from typing import Annotated

from aiogram.types import CallbackQuery,Message
from aiogram import Router,F, Bot
from aiogram.fsm.context import FSMContext

from app.bot.utils import get_quit_profile, get_profile_content, get_registration_info,\
      get_how_the_bot_works, get_reg_start_info, get_without_sub_info, get_basic_sub_info,\
          get_premium_sub_info, get_basic_subscription_price, get_premium_subscription_price
from app.bot.keyboard import inline
from app.services import UserService
from app.bot.states.registration import RegistrationStatesGroup

from dishka.integrations.aiogram import inject, Depends

router = Router()

#! Main Menu
@router.callback_query(F.data == "main_menu")
async def menu_call(query: CallbackQuery):
    await query.message.edit_text("🔮Выберите действия по кнопкам ниже:", reply_markup=inline.main_menu)


#! Logging Out of Profile
@router.callback_query(F.data == "quit_profile")
async def quit_profile(query: CallbackQuery):
    await query.message.edit_text(get_quit_profile(), reply_markup=inline.quit_profile_kb_markup, disable_web_page_preview=True)


@router.callback_query(F.data == "pre_quit")
async def pre_quit_profile(query: CallbackQuery):
    await query.message.edit_text("""Вы уверены что хотите выйти? 👣
Восстановить аккаунт будет невозможно! ⚠️""",
                                  reply_markup=inline.log_out_for_sure_button)


@router.callback_query(F.data == "quit")
async def quit_profile(query: CallbackQuery):
    user_id = query.from_user.id
    await update_get_email_from(user_id, "None")
    await update_get_pwd_from(user_id, None)
    await update_sub(user_id, "none")
    await query.message.edit_text(text='''Вы успешно вышли из аккаунта! 🪫
Желаете создать новый?''', reply_markup=inline.profile_repeat_registration_kb_markup)


#! How The Bot Works
@router.callback_query(F.data == "how_work")
async def how_work_call(query:CallbackQuery):
    await query.message.edit_text(get_how_the_bot_works(), reply_markup=inline.back_to_main_menu_markup)


#! Getting User Profile Content
@router.callback_query(F.data == "profile")
async def get_user_profile_info(query: CallbackQuery, user_service: Annotated[UserService, Depends()]):
    user_id = query.from_user.id
    email_is_filled = await user_service.user_email_is_filled(user_id)

    if email_is_filled:
        await query.message.edit_text(get_profile_content(),
                                      reply_markup=inline.change_profile_markup,
                                      disable_web_page_preview=True)
        
    else:
        await query.message.edit_text("К сожалению у вас еще нет аккаунта 🤷🏻‍\n️"
                                  "Чтобы смотреть свой профиль пройдите регистрацию ⬇️",
                                  reply_markup=inline.profile)


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
async def cancel_call(query: CallbackQuery):
    await query.message.delete()


#! Auto-Mailing call
@router.callback_query(F.data=="auto_mailing")
async def auto_mailing_call(query:CallbackQuery):
    await query.message.edit_text("📮 Выберите действия по кнопкам ниже:",reply_markup=inline_builder(
        ['✉️ Почты','🎹 Биты','⚙️ Настройки'],
        ['add_email','add_audio','settings'],
        [2,1]
    ))


#! Auto-Mailing Settings
@router.callback_query(F.data == "settings")
async def settings_call(query: CallbackQuery):
    info = await get_email_info(user_id=query.from_user.id)
    await query.message.edit_text("Выберите,что вы хотите изменить в письме\n"
                                  "<b>Сейчас ваше письмо выглядит так:</b>\n\n"
                                  f"•Заголовок: <u>{info[0]}</u>\n"
                                  f"•Описание: <u>{info[1]}</u>\n"
                                  f"•Ежедневное время отправки: <u>{info[2]}</u>\n"
                                  f"•Кол-во аудио в письме за раз: <u>{info[3]}</u>", reply_markup=inline_builder(
        ["Описание+заголовок", "Время отправки", "Кол-во аудио в сообщении"],
        ["description", "mail_time", "quantity"],
        [2, 1]
    ))


@router.callback_query(F.data == "quantity")
async def quantity_call(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Напиши число от 1 до 10 аудио в письме(рекомендуется 2)")
    await state.set_state(QuantyMail.quanty)


@router.callback_query(F.data == "description")
async def desc_call(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Напишите заголовок/тему к вашим будущим письмам")
    await state.set_state(MailDescription.header)


@router.callback_query(F.data == "mail_time")
async def mail_time_call(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Отправьте время в формате: (час):(минута) ")
    await state.set_state(QuantyMail.mail_time)


#! Self-Mailing
@router.callback_query(F.data == "self_mailing")
async def self_mailing_call(query:CallbackQuery,state:FSMContext):
    await query.message.answer("""Отправьте email-адреса артистов 📭 
    <blockquote>(через запятую либо с новой строки)</blockquote>""",
                               parse_mode='html')
    await state.set_state(Mailing.get_emails)


#! Audio-list Actions
@router.callback_query(F.data == "add_audio")
async def add_audio_call(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Отправьте аудио 🎵")
    await state.set_state(Mailing.get_audio)


@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Отправьте боту аудио, которое хотите удалить")
    await state.set_state(Del_audio.audio_to_del)
