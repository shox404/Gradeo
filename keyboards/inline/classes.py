from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def classes_keyboard(classes, method):
    """Generate a keyboard for selecting classes."""
    keyboard = [
        [
            InlineKeyboardButton(
                text=class_data["name"],
                callback_data=f"{method}_{class_data['id']}",
            )
            for class_data in classes[i : i + 3]
        ]
        for i in range(0, len(classes), 3)
    ]
    keyboard.append(
        [InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{method}")]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


manage_classes_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Add Class", callback_data="add_class"),
        ],
        [
            InlineKeyboardButton(text="Edit Class", callback_data="edit_class"),
            InlineKeyboardButton(text="Delete Class", callback_data="delete_class"),
        ],
    ]
)

estimate_student_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Set Mark", callback_data="set_mark"),
            InlineKeyboardButton(text="Delete Mark", callback_data="delete_mark"),
        ],
    ]
)


# async def classes_keyboard(classes, method):
#     """Create an inline keyboard with class buttons."""
#     buttons = [
#         InlineKeyboardButton(
#             text=class_item.get("name", "Undefined"),
#             callback_data=f"class_{method}_{class_item.get("id", "0")}",
#         )
#         for class_item in classes
#     ]

#     rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

#     text = ""
#     if method == "delete":
#         text = "_delete_class"
#     elif method == "edit":
#         text = "_edit_class"
#     elif method == "add_user":
#         text = "_add_user"

#     rows.append([InlineKeyboardButton(text="Cancel", callback_data=f"cancel{text}")])
#     return InlineKeyboardMarkup(inline_keyboard=rows)


edit_option_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Class", callback_data="manage_classes_edit_class_name"
            ),
            InlineKeyboardButton(
                text="Teacher", callback_data="manage_classes_edit_teacher_name"
            ),
        ],
        [
            InlineKeyboardButton(text="Cancel", callback_data="cancel_edit_class"),
        ],
    ]
)


delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Yes", callback_data="confirm_class_delete_yes"),
        ],
        [
            InlineKeyboardButton(text="No", callback_data="cancel_delete_class"),
        ],
    ]
)
