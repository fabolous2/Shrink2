from aiogram.fsm.state import StatesGroup, State

class SelfMailingStatesGroup(StatesGroup):
    WAIT_FOR_EMAILS = State()
    WAIT_FOR_AUDIOS = State()

