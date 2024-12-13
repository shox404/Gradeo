from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="confirm_class_delete_yes")],
        [InlineKeyboardButton(text="No", callback_data="confirm_class_delete_yes")],
    ]
)
