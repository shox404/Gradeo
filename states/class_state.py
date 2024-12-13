from aiogram.filters.state import State, StatesGroup


class ClassState(StatesGroup):
    name = State()
    teacher = State()
    manage_class = State()
    update_class_id = State()
    update_option = State()
    delete_class_id = State()
    confirm_delete = State()


class DeleteClass(StatesGroup):
    name = State()
    confirm_delete = State()
