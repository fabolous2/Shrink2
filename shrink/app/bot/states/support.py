from aiogram.fsm.state import StatesGroup, State


class SupportStatesGroup(StatesGroup):
    WAIT_FOR_REPORT = State()
