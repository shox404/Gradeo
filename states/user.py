from aiogram.filters.state import State, StatesGroup


class User(StatesGroup):
    fullname = State()
    role = State()
    username = State()
    user_id = State()


class UpdateUser(StatesGroup):
    user_id = State()
    edit_option = State()
    fullname = State()
    username = State()
    role = State()


class DeleteUser(StatesGroup):
    user_id = State()
    confirm_delete = State()
