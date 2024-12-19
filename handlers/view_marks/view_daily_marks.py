from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime, timezone
from firebase.config import db

view_daily_marks_router = Router()


async def get_user_role_and_class(user_id: str) -> tuple:
    user_ref = db.collection("users").document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get("role"), user_data.get("class")
    return None, None


@view_daily_marks_router.callback_query(F.data == "view_daily_marks")
async def handle_daily_marks(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    role, user_class_id = await get_user_role_and_class(user_id)
    print(role,user_class_id)
    if not role or not user_class_id:
        await callback.message.edit_text("❌ Unable to retrieve user information.")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(today)
    marks_ref = db.collection("marks")
    query = marks_ref.where("class_id", "==", user_class_id).where(
        "timestamp", ">=", today
    )
    if role == "Student":
        query = query.where("student_id", "==", user_id)

    marks_snapshot = query.get()
    print(marks_snapshot)

    if marks_snapshot:
        marks_text = f"<b>📅 Today's Marks ({today}):</b>\n\n"
        for mark in marks_snapshot:
            mark_data = mark.to_dict()
            subject_id = mark_data.get("subject_id", "Unknown Subject")
            student_name = mark_data.get("student_name", "Unknown Student")
            mark_value = mark_data.get("mark", "N/A")
            timestamp = mark_data.get("timestamp").strftime("%H:%M")

            subject_ref = db.collection("subjects").document(subject_id)
            subject_doc = subject_ref.get()
            subject_name = subject_doc.to_dict().get("name", "Unknown Subject")

            if role == "Student":
                marks_text += f"📝 {subject_name}: {mark_value} at {timestamp}\n"
            else:
                marks_text += (
                    f"📝 {subject_name} - {student_name}: {mark_value} at {timestamp}\n"
                )
    else:
        marks_text = "❌ No marks available for today."

    await callback.message.edit_text(marks_text)
