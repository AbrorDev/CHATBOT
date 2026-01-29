from aiogram.fsm.state import State, StatesGroup

class SettingsState(StatesGroup):
    language = State()