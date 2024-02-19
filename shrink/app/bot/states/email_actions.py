from aiogram.fsm.state import StatesGroup, State


class AddToEmailStatesGroup(StatesGroup):
    WAIT_FOR_ADD_EMAIL = State()
    

class DeletionEmailStatesGroup(StatesGroup):
    WAIT_FOR_DEL_EMAIL = State()
    
