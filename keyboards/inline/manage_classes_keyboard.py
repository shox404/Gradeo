from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

manage_classes_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Add Class", callback_data="add_class"),
            InlineKeyboardButton(text="Update Class", callback_data="update_class"),
        ],
        [
            InlineKeyboardButton(text="Delete Class", callback_data="delete_class"),
            InlineKeyboardButton(text="View Classes", callback_data="view_classes"),
        ],
    ]
)
