from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase.functions.subjects import get_all_subjects


def create_inline_button(text, callback_data) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def create_keyboard(rows):
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def users_keyboard(users, method):
    inline_keyboard = [
        [
            create_inline_button(
                f"{user['fullname']} ({user['username']})",
                f"student_{method}_{user['id']}",
            )
            for user in users[i : i + 2]
        ]
        for i in range(0, len(users), 2)
    ]
    inline_keyboard.append(
        [create_inline_button("⬅️ Назад", f"back_to_classes_{method}")]
    )
    return create_keyboard(inline_keyboard)


async def subject_keyboard(subjects, method):
    inline_keyboard = [
        [
            create_inline_button(
                (
                    subject["name"] if subject["name"] else "Неизвестный предмет"
                ),  # Default value if name is None or empty
                f"{method}_subject_{subject['id']}",
            )
            for subject in subjects[i : i + 2]
        ]
        for i in range(0, len(subjects), 2)
    ]
    if method != "delete_teacher":
        inline_keyboard.append(
            [create_inline_button("⬅️ Назад", f"back_to_classes_{method}")]
        )
    return create_keyboard(inline_keyboard)


async def teacher_keyboard(teachers, method):
    inline_keyboard = [
        [
            create_inline_button(
                f"{teacher['fullname']} ({teacher['username']})",
                f"teacher_{method}_{teacher['id']}",
            )
            for teacher in teachers[i : i + 2]
        ]
        for i in range(0, len(teachers), 2)
    ]
    inline_keyboard.append(
        [create_inline_button("⬅️ Назад", f"back_to_subjects_{method}")]
    )
    return create_keyboard(inline_keyboard)


async def subjects_keyboard():
    subjects = await get_all_subjects()
    inline_keyboard = [
        [
            create_inline_button(
                subject["name"] if subject["name"] else "Неизвестный предмет",
                f"subject_add_{subject['id']}",
            )
            for subject in subjects[i : i + 2]
        ]
        for i in range(0, len(subjects), 2)
    ]
    inline_keyboard.append([create_inline_button("Отмена", "cancel_add_user")])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def edit_options_keyboard(student_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                create_inline_button("Редактировать Ф.И.О.", f"edit_fullname_{student_id}"),
                create_inline_button("Редактировать Username", f"edit_username_{student_id}"),
            ],
            [create_inline_button("Изменить класс", f"change_class_{student_id}")],
            [create_inline_button("⬅️ Назад к студентам", "back_to_students")],
        ]
    )


def edit_teacher_options_keyboard(teacher_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                create_inline_button("Редактировать Ф.И.О.", f"edit_fullname_{teacher_id}"),
                create_inline_button("Редактировать Username", f"edit_username_{teacher_id}"),
            ],
            [create_inline_button("Редактировать должность", f"edit_position_{teacher_id}")],
            [create_inline_button("⬅️ Назад к преподавателям", "back_edit_to_teachers")],
        ]
    )


def cancel_keyboard():
    return create_keyboard([[create_inline_button("Отмена", "cancel_add_user")]])


manage_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Добавить пользователя", "add_user")],
        [
            create_inline_button("Редактировать пользователя", "edit_user"),
            create_inline_button("Удалить пользователя", "delete_user"),
        ],
    ]
)

edit_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Студент", "edit_student"),
            create_inline_button("Преподаватель", "edit_teacher"),
        ],
        [create_inline_button("⬅️ Назад", "back_to_manage_users")],
    ]
)

delete_user_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Студент", "delete_student"),
            create_inline_button("Преподаватель", "delete_teacher"),
        ],
        [create_inline_button("⬅️ Назад", "back_to_manage_users")],
    ]
)

delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Да", "confirm_user_delete_yes")],
        [create_inline_button("Нет", "cancel_delete_student")],
    ]
)

delete_teacher_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Да", "confirm_teacher_delete_yes")],
        [create_inline_button("Нет", "cancel_select_subject_delete_teacher")],
    ]
)
