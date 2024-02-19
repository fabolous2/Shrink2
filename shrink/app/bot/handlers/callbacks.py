from aiogram.types import CallbackQuery,Message
from aiogram import Router,F, Bot
from aiogram.fsm.context import FSMContext

from app.bot.utils import get_quit_profile
from app.bot.keyboard import inline

router = Router()


@router.callback_query(F.data == "main_menu")
async def menu_call(query: CallbackQuery):
    await query.message.edit_text("🔮Выберите действия по кнопкам ниже:", reply_markup=inline.main_menu)


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
Желаете создать новый?''',
                                  reply_markup=inline_builder(
                                      ["📇 Регистрация"],
                                      ["re_reg_gmail"]
                                  ))


#How Works
@router.callback_query(F.data=="how_work")
async def how_work_call(query:CallbackQuery):
    await query.message.edit_text( text='''
    📩 Shrink — сервис массовой рассылки почты для битмейкеров

    Как работает наш бот? (https://telegra.ph/Kak-rabotaet-Shrink-05-23)''', reply_markup=inline.back_to_main_menu_markup)


@router.callback_query(F.data=="profile")
async def my_profile(query:CallbackQuery):
    user_id = query.from_user.id
    if await get_email_from(user_id) != 'None':
        await query.message.edit_text(text=f"""🧸 Профиль {query.from_user.first_name}
———


✉️ Gmail:
└ {await get_email_from(user_id)}

🎟 Подписка: 
└ {await get_premium(user_id)}
——
<a href ="https://telegra.ph/Podklyuchaem-Google-Akkaunt--Le-Pair-02-01">О подписках </a>""",
                     reply_markup=inline_builder(
                         ["🧬 Сменить профиль", "⬅ Назад"],
                         ["quit_profile", "main_menu"],
                         [1, 1]),
                     disable_web_page_preview=True,
                     parse_mode='html')
    else:
        await query.message.edit_text("К сожалению у вас еще нет аккаунта 🤷🏻‍\n️"
                                  "Чтобы смотреть свой профиль пройдите регистрацию ⬇️",
                                  reply_markup=inline.profile)

#SUPPORT
@router.callback_query(F.data=="support")
async def support_call(query:CallbackQuery,state:FSMContext):
    print(query.from_user.id)
    await state.set_state(Sup.text)
    await query.message.answer("""👀 Опиши проблему, которая у тебя возникла ⬇️
<blockquote>Вопросы, предложения, сотрудничество тоже сюда!</blockquote>""",
                               parse_mode='html')


@router.callback_query(F.data=="sup_cancel")
async def sup_cancel_call(query:Message | CallbackQuery,state:FSMContext):
    state_data = await state.get_data()
    await state.update_data(photo='None')
    state_data["photo"] = 'None'
    formatted_text = []
    [
        formatted_text.append(f'{value}')
        for value in state_data.values()
    ]
    pattern=dict(text="<b>Подтвердите свою жалобу, она будет отправлена на обработку!</b>\n"
                                   f"<blockquote>{state_data["text"]}</blockquote>",reply_markup=inline_builder(
            ["✅ Подтвердить","🗑️ Отмена"],
            ["agree_sup","fully_sup_cancel"]
        ))

    if isinstance(query,CallbackQuery):
        await query.message.delete()
        await query.message.answer(**pattern)

    await state.set_state(Sup.send)


@router.callback_query(F.data == "fully_sup_cancel")
async def fully_sup_cancel(query: CallbackQuery):
    global user_id
    user_id = query.from_user.id
    await query.message.delete()
    await query.message.answer("🪬 Ваша жалоба успешно отменена!")
