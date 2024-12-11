from firebase.config import db


async def save_user_data(data):
    doc_ref = db.collection("users").document(str(data["user_id"]))
    doc_ref.set(data)


async def save_class_data(class_data: dict):
    class_ref = db.collection("classes").document(str(class_data["class_id"]))
    class_ref.set(class_data)


async def get_user_data(user_id: int):
    users_ref = db.collection("users")
    query = users_ref.where("user_id", "==", user_id).limit(1).get()

    if query:
        return query[0].to_dict()
    return None


async def update_user_data(user_id: int, updated_data: dict):
    users_ref = db.collection("users")
    query = users_ref.where("user_id", "==", user_id).limit(1).get()

    if query:
        user_ref = query[0].reference
        user_ref.update(updated_data)
