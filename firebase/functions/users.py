from firebase.config import db


async def save_user_data(data):
    doc_ref = db.collection("users").document(str(data["user_id"]))
    doc_ref.set(data)


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


async def delete_user_data(user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        user_ref.delete()
        return True
    else:
        return False


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
