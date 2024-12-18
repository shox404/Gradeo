from aiogram.fsm.state import State, StatesGroup


class Mark(StatesGroup):
    select_class = State()
    select_student = State()
    select_mark = State()
    confirm_deletion = State()
