from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def delete_confirmation_keyboard(route: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру подтверждения для действий удаления."""
    keyboard = [
        [
            InlineKeyboardButton(text="Да", callback_data=f"{route}_delete_yes"),
            InlineKeyboardButton(text="Отмена", callback_data=f"{route}_delete_cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_inline_button(text, callback_data):
    return InlineKeyboardButton(
        text=text or "Безымянный класс", callback_data=callback_data
    )


async def classes_keyboard(classes, method):
    keyboard = []
    for class_data in classes:
        class_name = class_data.get("name") or "Безымянный класс"
        class_id = class_data.get("id")
        if not class_id:
            continue

        keyboard.append([create_inline_button(class_name, f"{method}_{class_id}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


manage_classes_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Добавить класс", "add_class")],
        [
            create_inline_button("Редактировать класс", "edit_class"),
            create_inline_button("Удалить класс", "delete_class"),
        ],
    ]
)

manage_subjects_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Добавить предмет", "add_subject")],
        [
            create_inline_button("Редактировать предмет", "edit_subject"),
            create_inline_button("Удалить предмет", "delete_subject"),
        ],
    ]
)

estimate_student_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Установить оценку", "set_mark"),
        ],
        [
            create_inline_button("Удалить оценку", "delete_mark"),
        ],
    ]
)

edit_option_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            create_inline_button("Класс", "manage_classes_edit_class_name"),
            create_inline_button("Учитель", "manage_classes_edit_teacher_name"),
        ],
        [create_inline_button("Отмена", "cancel_edit_class")],
    ]
)

delete_confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [create_inline_button("Да", "confirm_class_delete_yes")],
        [create_inline_button("Нет", "cancel_delete_class")],
    ]
)
