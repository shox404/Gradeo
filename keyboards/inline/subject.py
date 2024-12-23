from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase.config import db


async def subjects_keyboard(subjects, route):
    keyboard = []
    row = []
    for i, subject in enumerate(subjects):
        name = subject.get("name")
        if not name or not isinstance(name, str):
            print(f"Invalid subject entry skipped: {subject}")
            continue

        row.append(
            InlineKeyboardButton(text=name, callback_data=f"{route}_{subject['id']}")
        )

        if len(row) == 2 or i == len(subjects) - 1:
            keyboard.append(row)
            row = []

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def edit_option_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Edit Name", callback_data="edit_name_of_subject"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Cancel", callback_data="cancel_edit_subject"
                ),
            ],
        ]
    )


async def get_subjects_keyboard() -> InlineKeyboardMarkup:
    subjects_ref = db.collection("subjects")
    subjects_snapshot = subjects_ref.get()

    subject_buttons = [
        [
            InlineKeyboardButton(
                text=subject.to_dict().get("name", "Unnamed Subject"),
                callback_data=f"view_by_subjects_{subject.id}",
            )
        ]
        for subject in subjects_snapshot
    ]

    subject_buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Back to Marks Menu", callback_data="back_to_marks_menu"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=subject_buttons)


def subject_keyboard(subjects) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=subj["name"], callback_data=f"select_subject_{subj['id']}"
            )
            for subj in subjects[i : i + 3]
        ]
        for i in range(0, len(subjects), 3)
    ]

    rows.append(
        [InlineKeyboardButton(text="Cancel", callback_data="cancel_select_subject")]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)

def delete_confirmation_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(text="Yes, delete", callback_data="confirm_subject_delete_yes"),
            InlineKeyboardButton(text="No, cancel", callback_data="cancel_delete_subject")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)