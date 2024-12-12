from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

manage_class_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton("Add Class", callback_data="add_class")],
        [InlineKeyboardButton("Edit Class", callback_data="edit_class")],
        [InlineKeyboardButton("Delete Class", callback_data="delete_class")],
    ]
)
