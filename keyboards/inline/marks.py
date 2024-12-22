from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

view_marks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📚 View Daily Marks", callback_data="view_daily_marks"
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="back_to_menu"),
        ],
    ]
)


def marks_keyboard(marks):
    """
    Creates an inline keyboard for selecting marks.
    """
    keyboard = [
        [
            InlineKeyboardButton(text=str(mark), callback_data=f"mark_{mark}")
            for mark in marks
        ]
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Back to students", callback_data="back_to_student_set_mark"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
