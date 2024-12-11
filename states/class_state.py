from aiogram.fsm.state import State, StatesGroup


class Class(StatesGroup):
    class_name = State()
    class_id = State()
    teacher_name = State()
    class_type = State()
