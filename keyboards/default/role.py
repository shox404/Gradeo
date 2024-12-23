from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Учитель")],
        [KeyboardButton(text="Студент")],
    ],
    resize_keyboard=True,
)
