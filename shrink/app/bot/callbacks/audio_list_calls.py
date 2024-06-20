import hashlib
from typing import Annotated
from aiogram_album import AlbumMessage
import html

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.media_group import MediaGroupBuilder

from app.bot.utils.bot_answer_text import (
    get_add_audio_text,
    get_del_audio_text,
    get_invalid_audio_format,
    get_empty_audio_list, 
    get_add_audio, 
    get_call_support, 
    get_del_audio,
    get_limit_audio_list,
    get_user_audio_list
)
from app.bot.states import AddAudiosStatesGroup, DelAudioStatesGroup

from app.bot.keyboard import inline, builder
from app.services import AudioService

from app.bot.handlers.commands import delete_messages

from dishka.integrations.aiogram import inject, Depends

from app.services.user_service import UserService

router = Router()

PAGE_SIZE = 8

async def show_audio_page(message, audio_list, current_page, page_count, query=None):
    start_index = current_page * PAGE_SIZE
    end_index = min((current_page + 1) * PAGE_SIZE, len(audio_list))

    audio_chunk = audio_list[start_index:end_index]

    buttons = []
    for audio_info in audio_chunk:
        file_id = audio_info['file_id']
        unique_id = hashlib.md5(file_id.encode()).hexdigest()
        audio_info['unique_id'] = unique_id
        buttons.append([InlineKeyboardButton(text=audio_info['audio_title'], callback_data=f"play_audio:{unique_id}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    pagination_buttons = inline.paginator_audio(current_page, page_count)
    keyboard.inline_keyboard.extend(pagination_buttons)

    keyboard.inline_keyboard.append([inline.add_audio_button, inline.delete_audio_button])
    keyboard.inline_keyboard.append([inline.back_to_settings_menu])

    if query:  
        await query.message.edit_text(
            get_user_audio_list(audios_count=len(audio_list)),
            reply_markup=keyboard
        )
    else:  
        await message.edit_text(
            get_user_audio_list(audios_count=len(audio_list)),
            reply_markup=keyboard
        )


@router.callback_query(F.data == "add_audio")
@inject
async def add_audio_call_to_db(
    query: CallbackQuery,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()],
) -> None:
    user_id = query.from_user.id
    audio_list = await audio_service.get_audio_list(user_id, is_extra=0)

    if audio_list:
        unique_audio_set = set()  
        unique_extra_audio_list = []  
        
        for audio in audio_list:
            if audio.name not in unique_audio_set:
                unique_audio_set.add(audio.name)
                unique_extra_audio_list.append({'file_id': audio.file_id, 'audio_title': audio.name})

        if unique_extra_audio_list:
            page_count = (len(unique_extra_audio_list) + PAGE_SIZE - 1) // PAGE_SIZE
    
        for audio_info in unique_extra_audio_list:
            file_id = audio_info['file_id']
            unique_id = hashlib.md5(file_id.encode()).hexdigest()
            audio_info['unique_id'] = unique_id

        await state.update_data(audio_list=unique_extra_audio_list)
        await show_audio_page(query.message, unique_extra_audio_list, 0, page_count)

    else:
        await query.message.edit_text(get_empty_audio_list(), reply_markup=inline.add_audio_kb_markup)
        
        
@router.callback_query(F.data.startswith("pag_audio:"))
async def handle_audio_pagination_action(query: CallbackQuery, state: FSMContext):

    data = query.data.split(":")[-1] 
    action, current_page, page_count = data.split(",")[:3] 
    current_page = int(current_page)
    page_count = int(page_count)

    state_data = await state.get_data()
    audio_list = state_data.get("audio_list")

    if action == 'prev':
        current_page -= 1
    elif action == 'next':
        current_page += 1

    await show_audio_page(query.message, audio_list, current_page, page_count, query)
    
def generate_unique_id(file_id):
    return hashlib.md5(file_id.encode()).hexdigest()


@router.callback_query(F.data.startswith("play_audio:"))
async def play_audio_callback(query: CallbackQuery, state: FSMContext):
    unique_id = query.data.split(":")[-1]
    state_data = await state.get_data()
    audio_list = state_data.get("audio_list")
    file_id = find_file_id_by_unique_id(audio_list, unique_id)
    if file_id:
        await query.message.answer_audio(file_id)
    else:
        await query.message.answer("Аудиофайл не найден.")
        
        
def find_file_id_by_unique_id(audio_list, unique_id):
    for audio_info in audio_list:
        if audio_info.get('unique_id') == unique_id:
            return audio_info.get('file_id')
    return None
    

@router.callback_query(F.data == "add_audio_to_db")
@inject
async def add_audio_call_to_db(
    query: CallbackQuery,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()], 
    user_service: Annotated[UserService, Depends()]
) -> None: 
    user_id = query.from_user.id
    audios = await audio_service.get_audio_list(user_id=user_id)
    audio_limit = await user_service.get_audio_limit(user_id=user_id)

    if audios and len(audios) == audio_limit:
        await query.answer(f"❗Достигнут лимит {audio_limit}/{audio_limit} аудио", show_alert=True)
    else:
        await query.message.edit_text(get_add_audio_text())
        await state.set_state(AddAudiosStatesGroup.WAIT_FOR_AUDIOS)


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.media_group_id)
@inject
async def audio_handler(
    album_message: AlbumMessage,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()], 
    user_service: Annotated[UserService, Depends()]
) -> None:
    user_id = album_message.from_user.id
    audio_list, left_audios  = await audio_service.create_audio_list(user_id=user_id, album_message=album_message)
    audio_list_from_db = await audio_service.get_audio_list(user_id, is_extra=0)
    audio_limit = await user_service.get_audio_limit(user_id=user_id)
    initial_audio_list = audio_list

    
    if audio_list_from_db:
        if left_audios:
            initial_audio_list = initial_audio_list[len(left_audios):]
            # user_audio_names = [audio.name for audio in audio_list_from_db]
            # initial_audio_list = [
            #     dictionary
            #     for dictionary in audio_list
            #     if dictionary['audio_name'] not in user_audio_names
            # ]
        try:
            unique_audio_set = set()  
            unique_auto_audio_list = []  
            for audio in audio_list_from_db:
                if audio.name not in unique_audio_set:
                    unique_audio_set.add(audio.name)
                    unique_auto_audio_list.append({'file_id': audio.file_id, 'audio_title': audio.name})

            unique_audio_list_names = [audio['audio_title'] for audio in unique_auto_audio_list] 
            final_list = []
            for audio in audio_list:
                if audio['audio_name'] not in unique_audio_list_names:
                    final_list.append(audio)

            if len(final_list) + len(audio_list_from_db) > audio_limit:
                left = audio_limit - len(audio_list_from_db)
                final_list = final_list[:left]
            # print(final_list)
  
            invalid_audios = list(filter(lambda audio: audio not in final_list, initial_audio_list))
            invalid_audio_names = [audio['audio_name'] for audio in invalid_audios]
            callback_datas = ["none_lol"] * len(invalid_audio_names)
            callback_datas.append("ok")
            invalid_audio_names.append("OK")
            # print(invalid_audios)
            await audio_service.add_audio(final_list)
            await album_message.answer(get_add_audio(len(final_list)), reply_markup=inline.view_audio_list_kb_markup)      
            if invalid_audios:
                await album_message.answer("❗️НЕ БЫЛИ ДОБАВЛЕНЫ:", reply_markup=builder.inline_builder(
                            text=invalid_audio_names,
                            callback_data=callback_datas,
                            sizes=1
                        ))  
        except Exception as _ex:
            print(_ex)
            await album_message.answer("❗️Что-то пошло не так. Обратитесь в поддержку")
        finally:
            await state.clear()
    else:
        try:
            await audio_service.add_audio(audio_list)
            await album_message.answer(get_add_audio(len(audio_list)), reply_markup=inline.view_audio_list_kb_markup)        
        except Exception as _ex:
            print(_ex)
            await album_message.answer(get_call_support())
        finally:
            await state.clear()


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.content_type == ContentType.AUDIO)
@inject
async def get_one_audio(
    audio_message: Message,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()],
    user_service: Annotated[UserService, Depends()], 
    bot: Bot
) -> None:
    user_id = audio_message.from_user.id
    index = await audio_service.generate_index_service(user_id=audio_message.from_user.id)
    audio_list_from_db = await audio_service.get_audio_list(user_id, is_extra=0)
    audio_limit = await user_service.get_audio_limit(user_id=user_id)
    
    audio_list = {
        'audio_id': audio_message.audio.file_id,
        'audio_name': audio_message.audio.file_name,
        'size': audio_message.audio.file_size,
        'user_id': audio_message.from_user.id,
        'audio_index': index[0]
    }

    if audio_list_from_db:
        if len(audio_list_from_db) + 1 > audio_limit:
            await audio_message.answer(get_limit_audio_list(audio_limit, len(audio_list_from_db)))
            await state.clear()
        elif audio_message.audio.mime_type != 'audio/mpeg':
            await audio_message.answer(get_invalid_audio_format())
        else:
            try:
                last_message_id = audio_message.message_id - 1
                await delete_messages(audio_message.chat.id, [last_message_id, audio_message.message_id], bot)
                audio_names_from_db = [audio.name for audio in audio_list_from_db]

                if audio_list['audio_name'] not in audio_names_from_db:
                    await audio_service.add_audio(audio_list)
                    await audio_message.answer(get_add_audio(1), reply_markup=inline.view_audio_list_kb_markup)
                else:
                    await audio_message.answer(get_add_audio(0), reply_markup=inline.view_audio_list_kb_markup)
                    await audio_message.answer("❗НЕ БЫЛО ДОБАВЛЕНО", reply_markup=builder.inline_builder(
                        text=[f"{audio_message.audio.file_name}", "OK"],
                        callback_data=["none_lol", "ok"],
                        sizes=1
                    ))
            except Exception as _ex:
                print(_ex)
                await audio_message.answer("❗️Что-то пошло не так. Обратитесь в поддержку")
            finally:
                await state.clear()
    else:
        try:
            last_message_id = audio_message.message_id - 1
            await delete_messages(audio_message.chat.id, [last_message_id, audio_message.message_id], bot)

            await audio_service.add_audio(audio_list)
            await audio_message.answer(get_add_audio(1), reply_markup=inline.view_audio_list_kb_markup)
        except Exception as _ex:
            print(_ex)
            await audio_message.answer(get_call_support())
        finally:
            await state.clear()

@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, ~F.content_type.in_({'audio','media_group_id'}))
async def cancel_update_audio(message: Message) -> None:
    await message.answer(get_invalid_audio_format())


@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.edit_text((get_del_audio_text()))
    await state.set_state(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL)
    
    
@router.message(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL, F.content_type == ContentType.AUDIO)
@inject
async def del_singleaudio_call(
    message: Message,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()],
    bot: Bot
) -> None:
    audio = message.audio
    if audio:
        last_message_id = message.message_id - 1
        await delete_messages(message.chat.id, [last_message_id, message.message_id], bot)
        await audio_service.delete_audio(user_id=message.from_user.id, filename=audio.file_name, size=audio.file_size)
        await message.answer(get_del_audio(1), reply_markup=inline.view_audio_list_kb_markup)
    else:
        await message.answer("Вы не отправили аудиофайл для удаления.")
    await state.clear()    
    

@router.message(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL, F.media_group_id)
@inject
async def delete_audio_handler(
    album_message: AlbumMessage,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    user_id = album_message.from_user.id
    audio_list = await audio_service.create_audio_list_deletion(user_id=user_id, album_message=album_message)
    
    audio_list_from_db = await audio_service.get_audio_list(user_id, is_extra=0)
    if audio_list_from_db:
        user_audio_names = [audio.name for audio in audio_list_from_db]
        audio_list = [
            dictionary
            for dictionary in audio_list
            if dictionary['audio_name'] in user_audio_names
        ]
    await audio_service.delete_audio_list(user_id, audio_list)
    await album_message.answer(get_del_audio(len(audio_list)), reply_markup=inline.view_audio_list_kb_markup)
    await state.clear()  
    
    

@router.callback_query(F.data == "edit_audios")
@inject
async def get_audio_list_call(
    query: CallbackQuery,
    audio_service: Annotated[AudioService, Depends()],
    bot: Bot
) -> None:
    user_id = query.from_user.id
    audio_list = await audio_service.get_audio_list(user_id)

    if audio_list:
        chunks = [audio_list[i:i + 10] for i in range(0, len(audio_list), 10)]
        await query.answer("Вот ваш список аудио:")

        for audio_chunk in chunks:
            media_group = MediaGroupBuilder()
            [
                media_group.add_audio(media=audio)
                for audio in audio_chunk
            ]
            await bot.send_media_group(user_id, media_group.build())

        await query.answer("Можете выбрать действие ниже", reply_markup=inline.choose_audio_actions_kb_markup)

    else:
        await query.answer(get_empty_audio_list(), reply_markup=inline.add_audio_kb_markup)