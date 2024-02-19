from aiogram.fsm.state import StatesGroup, State


class RegistrationStatesGroup(StatesGroup):
    WAIT_FOR_EMAIL = State()
    WAIT_FOR_PASSWORD = State()
    