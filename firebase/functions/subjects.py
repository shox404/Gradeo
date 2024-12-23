from firebase.config import db


async def delete_subject_data(subject_id: str) -> bool:
    """Deletes a subject from the database."""
    try:
        from firebase_admin import firestore

        db = firestore.client()

        subject_ref = db.collection("subjects").document(subject_id)

        if not subject_ref.get().exists:
            return False

        subject_ref.delete()
        return True
    except Exception as e:
        print(f"Error deleting subject: {e}")
        return False


async def save_subject_data(data: dict):
    """Save subject data with an auto-generated unique ID."""
    name = data.get("name")

    db.collection("subjects").add({"name": name})
    return True


async def update_subject(id: str, updated_data: dict):
    """Update subject data by subject ID."""
    try:
        ref = db.collection("subjects").document(id)
        doc = ref.get()

        if doc.exists:
            ref.update(updated_data)
            return True
        else:
            return False

    except Exception as e:
        return False


async def get_all_subjects() -> list:
    """
    Retrieve all subjects from the database.
    """
    subjects_ref = db.collection("subjects")
    subjects_snapshot = subjects_ref.get()

    subjects = []
    for subject in subjects_snapshot:
        subject_data = subject.to_dict()
        subject_data["id"] = subject.id
        subjects.append(subject_data)

    return subjects


async def get_subject_by_id(subject_id: str):
    ref = db.collection("subjects").document(subject_id)

    subject_data = ref.get()

    if subject_data.exists:
        return subject_data.to_dict()
    return None
