from aiogram.filters.state import State, StatesGroup


class ClassState(StatesGroup):
    name = State()
    teacher = State()
    edit_choice = State()
    edit_option = State()
    new_name = State()
    new_class_name = State()
    new_teacher = State()
    new_class_teacher = State()
    confirm_delete = State()
    

class DeleteClass(StatesGroup):
    name = State()
    confirm_delete = State()
