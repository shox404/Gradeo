from firebase.config import db


async def get_user_data(user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None


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
