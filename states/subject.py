from aiogram.filters.state import State, StatesGroup

class Subject(StatesGroup):
    name = State()
    
    edit_choice = State()
    edit_option = State()
    edit_new_name = State()
    
    delete_confirm = State()
