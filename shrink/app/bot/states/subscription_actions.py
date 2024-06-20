from aiogram.fsm.state import StatesGroup, State


class SubscriptionActionsStatesGroup(StatesGroup):
    WAIT_FOR_SUBSCRIPTION_TYPE = State()


class SubscriptionIssuingSG(StatesGroup):
    IDENTIFIER = State()
    TYPE = State()
    DURATION = State()
