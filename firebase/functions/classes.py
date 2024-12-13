from firebase.config import db


async def save_class_data(class_data: dict):
    name = class_data.get("name")
    teacher = class_data.get("teacher")

    if not name:
        raise ValueError("Class name is required to save class data.")

    class_ref = db.collection("classes").document(name)
    class_ref.set({"name": name, "teacher": teacher})


async def get_class_data(class_name: str):
    try:
        class_ref = db.collection("classes").document(class_name)
        class_doc = class_ref.get()

        if class_doc.exists:
            class_data = class_doc.to_dict()
            class_data["id"] = class_doc.id
            return class_data
        return None
    except Exception as e:
        print(f"Error fetching class data by name: {e}")
        return None


async def update_class_data(class_name: str, updated_data: dict):
    try:
        class_ref = db.collection("classes").document(class_name)
        class_doc = class_ref.get()

        if class_doc.exists:
            class_ref.update(updated_data)
            return True
        return False
    except Exception as e:
        print(f"Error updating class data: {e}")
        return False


async def delete_class_data(class_name: str):
    try:
        class_ref = db.collection("classes").document(class_name)
        class_doc = class_ref.get()

        if class_doc.exists:
            class_ref.delete()
            return True
        return False
    except Exception as e:
        print(f"Error deleting class data: {e}")
        return False


async def get_all_classes():
    try:
        class_collection = db.collection("classes")
        class_docs = class_collection.stream()

        classes = []
        for doc in class_docs:
            class_data = doc.to_dict()
            classes.append(
                {"name": doc.id, "teacher": class_data.get("teacher", "Unknown")}
            )
        return classes
    except Exception as e:
        print(f"Error fetching all classes: {e}")
        return []
