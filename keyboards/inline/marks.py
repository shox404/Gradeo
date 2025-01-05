from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

view_marks_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📚 ежедневные оценки", callback_data="view_daily_marks"
            )
        ],
        [
            InlineKeyboardButton(
                text="📚 оценки за четверть", callback_data="view_quarter_marks"
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


def marks_keyboard_with_cancel(marks, callback_prefix: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{mark['subject']} - {mark['mark']}",
                callback_data=f"{callback_prefix}_mark_{mark['id']}",
            )
        ]
        for mark in marks
    ]
    keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_{callback_prefix}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да", callback_data=f"{callback_prefix}_yes"
                ),
                InlineKeyboardButton(
                    text="Нет", callback_data=f"cancel_{callback_prefix}"
                ),
            ]
        ]
    )
