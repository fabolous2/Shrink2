from aiogram.fsm.state import StatesGroup, State


class SupportStatesGroup(StatesGroup):
    WAIT_FOR_REPORT = State()
    WAIT_FOR_SCREEN_OPTIONAL = State()
    ADMIN_CHECKING = State()
    SENDING = State()
