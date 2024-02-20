from aiogram.fsm.state import StatesGroup, State

class DelAudioStatesGroup(StatesGroup):
    WAIT_FOR_AUDIOS_TO_DEL = State()

class AddAudiosStatesGroup(StatesGroup):
    WAIT_FOR_AUDIOS = State()