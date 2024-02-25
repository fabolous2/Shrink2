from typing import Annotated
from aiogram_album import AlbumMessage

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Chat, Message

from app.bot.utils import get_add_audio_text, get_del_audio_text
from app.bot.states import AddAudiosStatesGroup, DelAudioStatesGroup

from app.bot.keyboard import inline
from app.services import AudioService

from dishka.integrations.aiogram import inject, Depends

router = Router()


# TODO: Audio Additing
@router.callback_query(F.data == "add_audio")
async def add_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_add_audio_text())
    await state.set_state(AddAudiosStatesGroup.WAIT_FOR_AUDIOS)


@router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.media_group_id)
@inject
async def audio_handler(
    message: AlbumMessage,
    state: FSMContext,
    audio_service: Annotated[AudioService, Depends()]
) -> None:
    audio_info = []
    user_id = None

    for audio_message in message:
        user_id = audio_message.from_user.id

        files_data = {
            'file_id': audio_message.audio.file_id,
            'name': audio_message.audio.file_name,
            'size': audio_message.audio.file_size,
            'user_id': user_id
        }
        audio_info.append(files_data)
    
    print(audio_info)
    await audio_service.add_audio(audio_info)

    try:
        await message.answer("Вы успешно обновили свой список аудио\nДля его просмотра воспользуйтесь коммандой\n"
                                "/audio_list")
        
    except Exception:
        await message.answer("Что то пошло не так, попробуйте обратиться в поддержку \n/support ")

    await state.clear()


# @router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, F.audio)
# async def get_single_audio(message: Message, state: FSMContext) -> None:
#     files_data = {}
#     audio_info = []
#     user_id = message.from_user.id

#     files_data["file_id"] = message.audio.file_id
#     files_data["name"] = message.audio.file_name.replace(" ", "")
#     files_data["size"] = message.audio.file_size
#     files_data["quant"] = 0
#     audio_info.append(files_data["file_id"] + ' ' + files_data['name'] + ' ' + str(files_data['size']) + ' ' + '0')
#     try:
#         await update_audio_file(user_id,audio_info)


#         await message.answer("Вы успешно обновили свой список аудио\nДля его просмотра воспользуйтесь коммандой\n"
#                          "/audio_list",
#                          reply_markup=reply.start_markup)
#         # else:
#         #     await message.answer("Ваш список не обновился. Возможно вы отправили боту уже существующее аудио в вашем списке."
#         #                          "Или же неправильный формат(поддерживается только mp3)\n"
#         #                          "Поддержка - /support")
#     except Exception:
#         await message.answer("Что то пошло не так, попробуйте обратиться в поддержку \n/support ")
#     await state.clear()


# @router.message(AddAudiosStatesGroup.WAIT_FOR_AUDIOS, ~F.content_type.in_({'audio','media_group_id'}))
# async def cancel_update_audio(message: Message):
#     await message.answer("Вы отправили неправильный формат файла(поддерживается только mp3")


#TODO: Audio Deleting
@router.callback_query(F.data == "del_audio")
async def del_audio_call(query: CallbackQuery, state: FSMContext) -> None:
    await query.message.answer(get_del_audio_text())
    await state.set_state(DelAudioStatesGroup.WAIT_FOR_AUDIOS_TO_DEL)
