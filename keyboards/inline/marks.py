from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

view_marks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📚 View Daily Marks", callback_data="view_daily_marks"
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu"),
        ],
    ]
)
