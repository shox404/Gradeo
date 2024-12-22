from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from firebase.config import db


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
