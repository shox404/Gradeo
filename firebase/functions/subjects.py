from firebase.config import db


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
