from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    language = State()
    phone = State()