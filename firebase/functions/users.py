from firebase.config import db


async def get_user_data(user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None


async def update_teacher_data(teacher_id: str, update_data: dict) -> None:
    """
    Update a teacher's data in the Firestore database.
    """
    db = firestore.client()
    teacher_ref = db.collection("users").document(teacher_id)

    teacher_ref.update(update_data)


async def get_teachers_by_subject(subject_id: str) -> list:
    """
    Fetches a list of teachers associated with a given subject.
    """
    db = firestore.client()
    teachers_ref = db.collection("users")

    query = teachers_ref.where("position", "==", subject_id)
    results = query.stream()

    teachers = []
    for doc in results:
        teacher = doc.to_dict()
        teacher["id"] = doc.id
        teachers.append(teacher)

    return teachers


async def get_teacher_data(teacher_id: str) -> dict:
    """
    Fetch teacher data by ID from the database.
    """
    from firebase_admin import firestore

    db = firestore.client()
    teacher_ref = db.collection("users").document(teacher_id)
    teacher_snapshot = teacher_ref.get()

    if teacher_snapshot.exists:
        return teacher_snapshot.to_dict()
    else:
        return None


from firebase_admin import firestore


async def get_all_teachers():
    """Retrieve all teachers from the database."""
    db = firestore.client()
    teachers_ref = db.collection("users")
    query = teachers_ref.where("role", "==", "Teacher")
    try:
        teachers = []
        docs = query.stream()
        for doc in docs:
            teacher = doc.to_dict()
            teacher["id"] = doc.id
            teachers.append(teacher)
        return teachers
    except Exception as e:
        print(f"Error fetching teachers: {e}")
        return []


async def get_all_users():
    user_collection = db.collection("users")
    user_docs = user_collection.stream()

    users = []
    for doc in user_docs:
        user_data = doc.to_dict()
        users.append(
            {
                "id": doc.id,
                "fullname": user_data.get("fullname", "Unknown"),
                "username": user_data.get("username", "N/A"),
            }
        )
    return users


async def get_users_in_class(class_id):
    try:
        users_query = db.collection("users").where("class", "==", class_id).stream()

        users = []
        for user_doc in users_query:
            user_data = user_doc.to_dict()
            user_data["id"] = user_doc.id
            users.append(user_data)

        return users

    except Exception as e:
        print(f"Error fetching users in class {class_id}: {e}")
        return []


async def save_user_data(data):
    doc_ref = db.collection("users").document(str(data["user_id"]))
    doc_ref.set(data)


async def update_user_data(user_id: int, updated_data: dict):
    user_ref = db.collection("users").document(str(user_id))
    user_ref.update(updated_data)


async def delete_user_data(user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        user_ref.delete()
        return True
    else:
        return False
