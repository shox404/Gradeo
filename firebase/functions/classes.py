from firebase.config import db


async def save_class_data(class_data: dict):
    """Save class data with an auto-generated unique ID."""
    name = class_data.get("name")
    teacher = class_data.get("teacher")

    db.collection("classes").add({"name": name, "teacher": teacher})


async def get_class_data(id):
    """Retrieve class data by class ID."""
    try:
        class_ref = db.collection("classes").document(str(id))
        class_doc = class_ref.get()

        if class_doc.exists:
            class_data = class_doc.to_dict()
            class_data["id"] = class_doc.id
            return class_data
        else:
            return None
    except Exception as e:
        return None


async def update_class_data(class_id: str, updated_data: dict):
    """Update class data by class ID."""
    try:
        class_ref = db.collection("classes").document(class_id)
        class_doc = class_ref.get()

        if class_doc.exists:
            class_ref.update(updated_data)
            return True
        else:
            return False

    except Exception as e:
        return False


async def delete_class_data(class_id: str):
    """Delete class data by class ID."""
    try:
        class_ref = db.collection("classes").document(class_id)
        class_doc = class_ref.get()

        if class_doc.exists:
            class_ref.delete()
            return True
        else:
            return False

    except Exception as e:
        return False


async def get_all_classes():
    """Fetch all classes."""
    try:
        class_collection = db.collection("classes")
        class_docs = class_collection.stream()

        classes = []
        for doc in class_docs:
            class_data = doc.to_dict()
            classes.append(
                {
                    "id": doc.id,
                    "name": class_data.get("name"),
                    "teacher": class_data.get("teacher", "Unknown"),
                }
            )

        return classes
    except Exception as e:
        return []
