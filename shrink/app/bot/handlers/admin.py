from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.bot.keyboard import inline

admin = Router()


class Newsletter(StatesGroup):
    message = State()
    photo = State()
    confirm = State()


class AdminProtect(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [6644596826]


@admin.callback_query(AdminProtect(), F.data.in_(["menu", "menu_after_photo"]))
@admin.message(AdminProtect(), Command('apanel'))
async def apanel(message: Message | CallbackQuery):
    if isinstance(message, Message):
        await message.answer("Возможные комманды:",
                             reply_markup=inline_builder(
                                 ['📪 Рассылка'],
                                 ['newsletter'],
                             ))
    else:
        if message.data == "menu":
            await message.message.edit_text("Возможные комманды:",
                                            reply_markup=inline_builder(
                                                ['📪 Рассылка'],
                                                ['newsletter'],
                                            ))
        else:
            await message.message.answer("Возможные комманды:",
                                         reply_markup=inline_builder(
                                             ['📪 Рассылка'],
                                             ['newsletter'],
                                         ))


@admin.callback_query(AdminProtect(), F.data == 'newsletter')
async def newsletter(query: CallbackQuery, state: FSMContext):
    await state.set_state(Newsletter.message)
    await query.message.answer("Введите сообщение, которое нужно разослать пользователям")


@admin.message(AdminProtect(), Newsletter.message)
async def newsletter_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await state.set_state(Newsletter.photo)
    await message.answer("📷 Можете приложить скриншот (не обязательно)", reply_markup=inline_builder(
        ["📮 Отправить сейчас"],
        ["sup_cancel_admin"],
        [1]
    ))


@admin.message(AdminProtect(), Newsletter.photo, F.photo)
async def newsletter_photo(message: Message, state: FSMContext):
    await message.delete()
    photo_file_id = message.photo[-1].file_id
    state_data = await state.get_data()
    await state.update_data(photo=photo_file_id)
    state_data["photo"] = photo_file_id
    await state.update_data(photo=state_data['photo'])
    await message.answer_photo(state_data['photo'],
                               f"{state_data['message']}\n"
                               f"<blockquote>Уверены что хотите разослать это сообщение "
                               f"{len(await get_users())} пользователям </blockquote>",
                               reply_markup=inline_builder(
                                   ["✅ Разослать", "❌ Отмена"],
                                   ["confirm", "menu_after_photo"],
                                   [1]
                               ))
    await state.set_state(Newsletter.confirm)


@admin.message(AdminProtect(), Newsletter.photo, ~F.photo)
async def failed_photo(message: Message):
    await message.answer("❗️Неверный формат❗️")


@admin.callback_query(AdminProtect(), F.data == 'sup_cancel_admin')
async def newsletter_sup_cancel(message: CallbackQuery | Message, state: FSMContext):
    state_data = await state.get_data()
    await state.update_data(message=state_data['message'],
                            photo='None')
    await message.message.answer(f"{state_data['message']}\n"
                                 f"<blockquote>Уверены что хотите разослать это сообщение "
                                 f"{len(await get_users())} пользователям </blockquote>",
                                 reply_markup=inline_builder(
                                     ["✅ Разослать", "❌ Отмена"],
                                     ["confirm", "menu"],
                                     [1]
                                 ))
    await state.set_state(Newsletter.confirm)


@admin.callback_query(AdminProtect(), Newsletter.confirm, F.data == "confirm")
async def newsletter_confirm(query: CallbackQuery, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    await state.update_data(message=state_data['message'],
                            photo=state_data['photo'])

    if state_data["photo"] != "None":
        await query.message.answer("Подождите... Идет рассылка.")
        for user in await get_users():
            await bot.send_photo(chat_id=user,
                                 photo=state_data['photo'],
                                 caption=state_data['message'])
        await query.message.answer("Рассылка успешно завершена.")
    else:
        await query.message.answer("Подождите... Идет рассылка.")
        for user in await get_users():
            await bot.send_message(user,
                                   state_data['message'])
        await query.message.answer("Рассылка успешно завершена.")
    await state.clear()
