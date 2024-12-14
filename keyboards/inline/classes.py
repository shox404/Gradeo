from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def classes_keyboard(classes, method):
    """
    Create an inline keyboard with class buttons.
    :param classes: A list of dictionaries containing class data.
    """
    buttons = [
        InlineKeyboardButton(
            text=class_item.get("name", "Undefined"),
            callback_data=f"class_{method}_{class_item.get("id", "0")}",
        )
        for class_item in classes
    ]

    rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

    text = ""
    if method == "delete":
        text = "_delete_class"
    elif method == "edit":
        text = "_edit_class"

    rows.append([InlineKeyboardButton(text="Cancel", callback_data=f"cancel{text}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


edit_option_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Class", callback_data="edit_class_name"),
            InlineKeyboardButton(text="Teacher", callback_data="edit_teacher_name"),
        ]
    ]
)


delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="confirm_class_delete_yes")],
        [InlineKeyboardButton(text="No", callback_data="confirm_class_delete_no")],
    ]
)
