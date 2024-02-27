from typing import Annotated
from aiogram_album import AlbumMessage

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, Message, ContentType
from aiogram.utils.media_group import MediaGroupBuilder

from app.bot.utils import (
    get_add_audio_text,
    get_del_audio_text,
    get_successful_update_audio,
    get_wrong_update_audio,
    get_invalid_audio_format
)
from app.bot.states import AddAudiosStatesGroup, DelAudioStatesGroup

from app.bot.keyboard import inline
from app.services import AudioService

from dishka.integrations.aiogram import inject, Depends

router = Router()


@router.callback_query(F.data == "add_audio")
async def add_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_add_audio_text())
    await state.set_state(AddAudiosStatesGroup.WAIT_FOR_AUDIOS)


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.media_group_id)
@inject
async def audio_handler(
    album_message: AlbumMessage,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    audio_info = [
        {
        'file_id': audio_message.audio.file_id,
        'name': audio_message.audio.file_name,
        'size': audio_message.audio.file_size,
        'user_id': audio_message.from_user.id
        }
        for audio_message in album_message
    ]

    try:
        await audio_service.add_audio(audio_info)
        await album_message.answer("Вы успешно обновили свой список аудио\nДля его просмотра воспользуйтесь коммандой\n"
                                "/audio_list")
        
    except Exception:
        await album_message.answer("Что то пошло не так, попробуйте обратиться в поддержку \n/support ")

    await state.clear()


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.content_type == ContentType.AUDIO)
@inject
async def get_one_audio(
    audio_message: Message,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    audio_info = {
        'file_id': audio_message.audio.file_id,
        'name': audio_message.audio.file_name,
        'size': audio_message.audio.file_size,
        'user_id': audio_message.from_user.id
    }

    try:
        await audio_service.add_audio(audio_info)
        await audio_message.answer()
        
    except Exception:
        await audio_message.answer("Что то пошло не так, попробуйте обратиться в поддержку \n/support ")
    await state.clear()


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, ~F.content_type.in_({'audio','media_group_id'}))
async def cancel_update_audio(message: Message):
    await message.answer("Вы отправили неправильный формат файла(поддерживается только mp3")


#TODO: Audio Deleting
@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_del_audio_text())
    await state.set_state(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL)


@router.callback_query(F.data == "edit_audios")
@inject
async def get_audio_list_call(
    query: CallbackQuery,
    audio_service: Annotated[AudioService, Depends()],
    bot: Bot
) -> None:
    user_id = query.from_user.id
    audio_list = await audio_service.get_audio_list(user_id)
    print(audio_list)
    
    if audio_list:
        # audio_list=list(filter(lambda x: len(x)==71 or len(x)==72, get_audio_file(user_id).split()))
        chunks = [audio_list[i:i + 10] for i in range(0, len(audio_list), 10)]
        await query.answer("Вот ваш список аудио:")

        for audio_chunk in chunks:
            media_group = MediaGroupBuilder()
            #добавление аудио в builder
            [
                media_group.add_audio(media=audio)
                for audio in audio_chunk
            ]
            await bot.send_media_group(user_id,media_group.build())

        await query.answer("Можете выбрать действие ниже", reply_markup=inline.choose_audio_actions_kb_markup)

    else:
        await query.answer("У вас нет аудио в списке(", reply_markup=inline.add_audio_kb_markup)