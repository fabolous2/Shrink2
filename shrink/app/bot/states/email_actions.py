from aiogram.fsm.state import StatesGroup, State


class AddToEmailStatesGroup(StatesGroup):
    WAIT_FOR_ADD_EMAIL = State()
    

class DeletionEmailStatesGroup(StatesGroup):
    WAIT_FOR_DEL_EMAIL = State()
    

class EmailQuantityStatesGroup(StatesGroup):
    WAIT_FOR_QUANTITY = State()


class EmailScheduleStatesGroup(StatesGroup):
    WAIT_FOR_TIME = State()


class EmailContentStatesGroup(StatesGroup):
    WAIT_FOR_DESCRIPTION = State()
    WAIT_FOR_SUBJECT = State()
    