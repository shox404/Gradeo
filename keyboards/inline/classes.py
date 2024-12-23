from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def delete_confirmation_keyboard(route: str) -> InlineKeyboardMarkup:
    """Creates a confirmation keyboard for delete actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="Yes", callback_data=f"{route}_delete_yes"),
            InlineKeyboardButton(text="Cancel", callback_data=f"{route}_delete_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_inline_button(text, callback_data):
    return InlineKeyboardButton(
        text=text or "Unnamed Class", callback_data=callback_data
    )


async def classes_keyboard(classes, method):
    keyboard = []
    for class_data in classes:
        class_name = class_data.get("name") or "Unnamed Class"
        class_id = class_data.get("id")
        if not class_id:
            continue

        keyboard.append([create_inline_button(class_name, f"{method}_{class_id}")])

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

manage_subjects_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Add Subject", "add_subject")],
        [
            create_inline_button("Edit Subject", "edit_subject"),
            create_inline_button("Delete Subject", "delete_subject"),
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
