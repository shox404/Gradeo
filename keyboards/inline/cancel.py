from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def cancel_keyboard(method: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data=f"cancel_{method}")]
        ]
    )
