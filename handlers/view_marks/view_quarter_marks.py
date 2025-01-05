from aiogram import Router, F
from aiogram.types import CallbackQuery
from firebase.config import db
from firebase.functions.users import get_user_data, get_user_role_and_class

view_quarter_marks = Router()


@view_quarter_marks.callback_query(F.data == "view_quarter_marks")
async def handle_monthly_marks(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    role, user_class_id = await get_user_role_and_class(user_id)

    if not role or not user_class_id:
        await callback.message.edit_text(
            "❌ Невозможно получить информацию о пользователе."
        )
        return

    marks_ref = db.collection("marks")
    query = marks_ref.where("class_id", "==", user_class_id)

    if role == "Student":
        query = query.where("student_id", "==", user_id)

    marks_snapshot = query.get()

    if marks_snapshot:
        marks_text = f"<b>📅 Результаты за месяц:</b>\n\n"
        subject_marks = {}
        total_marks = 0
        total_possible_marks = 0

        for mark in marks_snapshot:
            mark_data = mark.to_dict()
            teacher_data = await get_user_data(mark_data["teacher_id"])
            subject_id = teacher_data["position"]
            mark_value = mark_data.get("mark", 0)

            if subject_id not in subject_marks:
                subject_marks[subject_id] = []
            subject_marks[subject_id].append(mark_value)

            total_marks += mark_value
            total_possible_marks += 5 

        for subject_id, marks in subject_marks.items():
            subject_ref = db.collection("subjects").document(subject_id)
            subject_doc = subject_ref.get()

            if subject_doc.exists:
                subject = subject_doc.to_dict()
                subject_name = subject.get("name", "Неизвестный предмет")
            else:
                subject_name = "Неизвестный предмет"

            subject_total = sum(marks)
            subject_max = len(marks) * 5
            subject_percent = (subject_total / subject_max) * 100 if subject_max else 0

            marks_text += f"{subject_name}: <b>{subject_percent:.2f}%</b>\n"

        total_percent = (total_marks / total_possible_marks) * 100 if total_possible_marks else 0
        marks_text += f"\n<b>Общий результат:</b> <b>{total_percent:.2f}%</b>"
    else:
        marks_text = "❌ Результаты за месяц отсутствуют."

    await callback.message.edit_text(marks_text)
