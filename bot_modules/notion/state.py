from aiogram.fsm.state import StatesGroup, State


class NotionState(StatesGroup):
    typing_email_to_login = State()
    typing_name_to_login = State()
    not_logged = State()
    logged = State()
