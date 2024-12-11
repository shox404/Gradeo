from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Teacher")],
        [KeyboardButton(text="Student")],
    ],
    resize_keyboard=True,
)
