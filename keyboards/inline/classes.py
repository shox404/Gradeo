from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_inline_button(text: str, callback_data: str) -> InlineKeyboardButton:
    """Helper function to create an inline button."""
    return InlineKeyboardButton(text=text, callback_data=callback_data)


async def classes_keyboard(classes, method):
    """Generate a keyboard for selecting classes with pagination (3 buttons per row)."""
    keyboard = [
        [
            create_inline_button(class_data["name"], f"{method}_{class_data['id']}")
            for class_data in classes[i : i + 3]
        ]
        for i in range(0, len(classes), 3)
    ]
    keyboard.append([create_inline_button("Cancel", f"cancel_{method}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


manage_classes_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Add Class", "add_class")],
        [
            create_inline_button("Edit Class", "edit_class"),
            create_inline_button("Delete Class", "delete_class"),
        ],
    ]
)

estimate_student_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Set Mark", "set_mark"),
        ],
        [
            create_inline_button("Delete Mark", "delete_mark"),
        ],
    ]
)

edit_option_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Class", "manage_classes_edit_class_name"),
            create_inline_button("Teacher", "manage_classes_edit_teacher_name"),
        ],
        [create_inline_button("Cancel", "cancel_edit_class")],
    ]
)

delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Yes", "confirm_class_delete_yes")],
        [create_inline_button("No", "cancel_delete_class")],
    ]
)
