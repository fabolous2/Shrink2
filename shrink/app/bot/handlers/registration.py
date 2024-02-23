import re

from aiogram import Router,Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.bot.states import RegistrationStatesGroup

router=Router()


@router.message(RegistrationStatesGroup.WAIT_FOR_EMAIL)
async def form_email(message: Message, state: FSMContext, bot: Bot) -> None:
    email_reg = message.text
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not re.match(email_pattern, email_reg):
        await message.answer("Почта введена неверно. Попробуйте еще раз!")
        return
    
    await state.update_data(email_from=message.text)
    await state.set_state(RegistrationStatesGroup.WAIT_FOR_PASSWORD)
    # await update_get_email_from(message.from_user.id, email_reg)

    await bot.send_message(message.from_user.id,
                           text="Отлично! Теперь введите пароль приложения")


@router.message(RegistrationStatesGroup.WAIT_FOR_PASSWORD)
async def form_email(message: Message, state: FSMContext):
    password=message.text
    user_id=message.from_user.id

    if len(password) < 19 or len(password) > 20 or re.search(r'\d', password) or not password.count(" ") == 3:
        await message.answer("""""", reply_markup=inline.profile_reg)
        await update_get_email_from(message.from_user.id, "None")
        await state.clear()
    await state.update_data(password=password)
    data = await state.get_data()
    await state.clear()
    formatted_text=[]
    [
        formatted_text.append(value)
        for key,value in data.items()
    ]
    print(formatted_text)
    await update_get_pwd_from(message.from_user.id,formatted_text[1])
    await update_get_email_from(user_id, formatted_text[0])

    await message.answer("Поздравляю, вы успешно вошли в аккаунт!")

    await message.answer(text=f"""🧸 Профиль {message.from_user.first_name}
———


✉️ Gmail:
└ {await get_email_from(user_id)}

🎟 Подписка: 
└ {await get_premium(user_id)}
——
<a href ="https://telegra.ph/Podpiska-na-Be-Twin-02-09">О подписках </a>""",
                     reply_markup=builder.inline_builder(
                         ["🧬 Сменить профиль", "⬅ Назад"],
                         ["quit_profile", "main_menu"],
                         [1, 1]),
                         disable_web_page_preview=True,
                         parse_mode='html')


@router.message(Re_reg.re_reg_gmail)
async def re_reg_email(message: Message, state: FSMContext, bot: Bot):
    gmail_new = message.text
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_pattern, gmail_new):
        await message.answer("Почта введена неверно. Попробуйте еще раз!")
        return
    await state.update_data(re_reg_email=gmail_new)
    await state.set_state(Re_reg.re_reg_pwd)
    await update_get_email_from(message.from_user.id, gmail_new)
    await bot.send_message(message.from_user.id,
                           text="Отлично! Теперь введите пароль приложения")


@router.message(Re_reg.re_reg_pwd)
async def re_reg_email(message: Message, state: FSMContext):
    password = message.text
    user_id = message.from_user.id
    if len(password) < 19 or len(password) > 20 or re.search(r'\d', password) or not password.count(" ") == 3:
        await message.answer("""Что-то пошло не так 😩 
Проверьте правильность написания почты и пароля приложения и повторите попытку""", reply_markup=inline.profile_reg)
        await update_get_email_from(message.from_user.id, "None")
        await state.clear()
    await state.update_data(password=password)
    data = await state.get_data()
    await state.clear()
    formatted_text = []
    [
        formatted_text.append(value)
        for key, value in data.items()
    ]
    print(formatted_text)
    await update_get_pwd_from(message.from_user.id, formatted_text[1])
    await update_get_email_from(user_id, formatted_text[0])

    await message.answer("Поздравляю, вы успешно вошли в аккаунт!")

    await message.answer(text=f"""🧸 Профиль {message.from_user.first_name}
———


✉️ Gmail:
└ {await get_email_from(user_id)}

🎟 Подписка: 
└ {await get_premium(user_id)}
——
<a href ="https://telegra.ph/Podpiska-na-Be-Twin-02-09">О подписках </a>""",
                     reply_markup=builder.inline_builder(
                         ["🧬 Сменить профиль", "⬅ Назад"],
                         ["quit_profile", "main_menu"],
                         [1, 1]),
                     disable_web_page_preview=True,
                     parse_mode='html')


