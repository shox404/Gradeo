from firebase.config import db
from firebase_admin import firestore
from datetime import datetime, timedelta


async def save_mark(class_id: str, student_id: str, mark: int, teacher_id: int):
    marks_collection = db.collection("marks")
    mark_data = {
        "class_id": class_id,
        "student_id": student_id,
        "teacher_id": teacher_id,
        "mark": mark,
        "timestamp": firestore.SERVER_TIMESTAMP,
    }
    marks_collection.add(mark_data)
    return True


async def delete_mark(id):
    mark = db.collection("marks").document(id)
    mark.delete()


async def get_marks_for_student(student_id, teacher_id):
    marks_collection = db.collection("marks")
    one_month_ago = datetime.utcnow() - timedelta(days=30)

    query = (
        marks_collection.where("timestamp", ">=", one_month_ago)
        .where("student_id", "==", student_id)
        .where("teacher_id", "==", teacher_id)
    )

    docs = query.stream()
    marks = []

    for doc in docs:
        mark = doc.to_dict()
        mark["id"] = doc.id
        marks.append(mark)

    return marks
