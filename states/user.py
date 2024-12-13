from aiogram.filters.state import State, StatesGroup


class User(StatesGroup):
    fullname = State()
    role = State()
    username = State()
    student_class = State()
    user_id = State()
    position = State()


class UpdateStudent(StatesGroup):
    user_id = State()
    class_name = State()
    edit_option = State()
    fullname = State()
    username = State()
    position = State()
    role = State()


class UpdateTeacher(StatesGroup):
    user_id = State()
    class_name = State()
    edit_option = State()
    fullname = State()
    username = State()
    position = State()
    role = State()


class DeleteUser(StatesGroup):
    user_id = State()
    confirm_delete = State()

class DeleteTeacher(StatesGroup):
    user_id = State()
    confirm_delete = State()
