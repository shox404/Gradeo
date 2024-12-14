from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase.functions.users import get_all_users


async def get_user_keyboard():
    """
    Fetch the list of users and return a 3-column inline keyboard.
    """
    users = await get_all_users()

    buttons = []
    for i in range(0, len(users), 3):
        row = [
            InlineKeyboardButton(
                text=user.get("name", "Unnamed User"),
                callback_data=user.get("id", "0"),
            )
            for user in users[i : i + 3]
        ]
        buttons.append(row)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def get_edit_options_keyboard():
    """
    Generate an inline keyboard for editing options.
    """
    buttons = [
        InlineKeyboardButton(text="Full Name", callback_data="edit_option_fullname"),
        InlineKeyboardButton(text="Username", callback_data="edit_option_username"),
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

