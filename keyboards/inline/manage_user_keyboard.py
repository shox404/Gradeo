from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

manage_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="View Users", callback_data="view_users"), 
            InlineKeyboardButton(text="Add User", callback_data="add_user"),
        ],
        [
            InlineKeyboardButton(text="Edit User", callback_data="edit_user"),
            InlineKeyboardButton(text="Delete User", callback_data="delete_user"),
        ],

    ]
)
