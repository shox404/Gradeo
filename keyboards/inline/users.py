from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase.functions.subjects import get_all_subjects
from aiogram.types import InlineKeyboardMarkup


def create_keyboard(buttons):
    """
    Creates an InlineKeyboardMarkup object from a list of button rows.
    """
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def subject_keyboard(subjects, method):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{subject['name']}",
                callback_data=f"{method}_subject_{subject['id']}",
            )
            for subject in subjects[i : i + 3]
        ]
        for i in range(0, len(subjects), 3)
    ]

    inline_keyboard.append(
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_classes")]
    )

    return create_keyboard(inline_keyboard)


async def teacher_keyboard(teachers, method):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{teacher['fullname']} (@{teacher['username']})",
                callback_data=f"teacher_{method}_{teacher['id']}",
            )
            for teacher in teachers[i : i + 3]
        ]
        for i in range(0, len(teachers), 3)
    ]

    inline_keyboard.append(
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_subjects")]
    )

    return create_keyboard(inline_keyboard)


async def subject_keyboard(subjects, action):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=subject["name"], callback_data=f"subject_{action}_{subject['id']}"
            )
        ]
        for subject in subjects
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


manage_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Add User", callback_data="add_user")],
        [
            InlineKeyboardButton(text="Edit User", callback_data="edit_user"),
            InlineKeyboardButton(text="Delete User", callback_data="delete_user"),
        ],
    ]
)

edit_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Edit Student", callback_data="edit_student"),
            InlineKeyboardButton(text="Edit Teacher", callback_data="edit_teacher"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_manage_users")],
    ]
)

delete_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Delete Student", callback_data="delete_student"),
            InlineKeyboardButton(text="Delete Teacher", callback_data="delete_teacher"),
        ],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_manage_users")],
    ]
)

delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="confirm_user_delete_yes")],
        [InlineKeyboardButton(text="No", callback_data="confirm_user_delete_no")],
    ]
)

delete_teacher_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="confirm_teacher_delete_yes")],
        [InlineKeyboardButton(text="No", callback_data="confirm_teacher_delete_no")],
    ]
)


def create_keyboard(rows):
    """Helper function to create inline keyboards with multiple rows."""
    return InlineKeyboardMarkup(inline_keyboard=rows)


def class_selection_keyboard(classes: list, student_id: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for cls in classes:
        keyboard.add(
            InlineKeyboardButton(
                text=cls["class_name"],
                callback_data=f"change_class_{student_id}_{cls['class_id']}",
            )
        )
    keyboard.add(InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_students"))
    return keyboard


async def class_keyboard(classes, method):
    """
    Generate a keyboard for selecting classes.
    Each button represents a class with its name, arranged in 3 columns.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=class_data["name"],
                callback_data=f"class_{method}_{class_data['id']}",
            )
            for class_data in classes[i : i + 3]
        ]
        for i in range(0, len(classes), 3)
    ]
    return create_keyboard(inline_keyboard)


async def user_keyboard(users, method):
    """
    Generate a keyboard for selecting users within a class.
    Each button represents a user with their full name and username, arranged in 3 columns.
    """
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"{user['fullname']} (@{user['username']})",
                callback_data=f"student_{method}_{user['id']}",
            )
            for user in users[i : i + 3]
        ]
        for i in range(0, len(users), 3)
    ]

    inline_keyboard.append(
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_classes")]
    )

    return create_keyboard(inline_keyboard)


edit_options_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✏️ Edit Full Name", callback_data="edit_fullname"
            ),
            InlineKeyboardButton(text="✏️ Edit Username", callback_data="edit_username"),
        ],
        [
            InlineKeyboardButton(text="✏️ Edit Class", callback_data="edit_class"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_students")],
    ]
)


cancel_keyboard = create_keyboard(
    [[InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_add_user")]]
)


def student_edit_keyboard(student_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Full Name", callback_data=f"edit_fullname_{student_id}"
                ),
                InlineKeyboardButton(
                    text="✏️ Username", callback_data=f"edit_username_{student_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Change Class", callback_data=f"edit_class_{student_id}"
                )
            ],
            [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_students")],
        ]
    )


async def subjects_keyboard():
    subjects = await get_all_subjects()

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=subject["name"], callback_data=f"subject_add_{subject["id"]}"
            )
            for subject in subjects[i : i + 2]
        ]
        for i in range(0, len(subjects), 2)
    ]

    inline_keyboard.append(
        [InlineKeyboardButton(text="Cancel", callback_data="cancel_add_user")]
    )

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
