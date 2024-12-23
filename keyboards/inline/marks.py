from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

view_marks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📚 Просмотр ежедневных оценок", callback_data="view_daily_marks"
            )
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu"),
        ],
    ]
)


def marks_keyboard(marks):
    """
    Создает inline-клавиатуру для выбора оценок.
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
                text="⬅️ Назад к ученикам", callback_data="back_to_student_set_mark"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
