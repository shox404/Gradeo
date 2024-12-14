from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_keyboard(rows):
    """Helper function to create inline keyboards with multiple rows."""
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def class_keyboard(classes):
    """
    Generate a keyboard for selecting classes.
    Each button represents a class with its name, arranged in 3 columns.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=class_data["name"], callback_data=f"class_{class_data['id']}"
            )
            for class_data in classes[i : i + 3]
        ]
        for i in range(0, len(classes), 3)
    ]
    return create_keyboard(inline_keyboard)


async def user_keyboard(users):
    """
    Generate a keyboard for selecting users within a class.
    Each button represents a user with their full name and username, arranged in 3 columns.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{user['fullname']} (@{user['username']})",
                callback_data=f"student_{user['id']}",
            )
            for user in users[i : i + 3]
        ]
        for i in range(0, len(users), 3)
    ]
    inline_keyboard.append(
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_classes")]
    )
    return create_keyboard(inline_keyboard)


edit_options_keyboard = create_keyboard(
    [
        [
            InlineKeyboardButton(text="📝 Full Name", callback_data="edit_fullname"),
            InlineKeyboardButton(text="👤 Username", callback_data="edit_username"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_students")],
    ]
)

cancel_keyboard = create_keyboard(
    [[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_add_user")]]
)
