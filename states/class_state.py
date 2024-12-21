from aiogram.filters.state import State, StatesGroup

class ClassState(StatesGroup):
    name = State()
    teacher = State()
    
    edit_choice = State()
    edit_option = State()
    edit_new_name = State()
    edit_new_teacher = State()
    
    delete_confirm = State()
