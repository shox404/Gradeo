from aiogram.types import CallbackQuery
from aiogram import Router
from firebase.functions.users import get_all_users
from utils.detect_admin import is_admin

view_users_router = Router()


@view_users_router.callback_query(lambda c: c.data == "view_users")
async def view_users(callback_query: CallbackQuery):
    if await is_admin(callback_query):
        users = await get_all_users()
        if not users:
            await callback_query.message.answer(
                "📋 <b>No users found in the system.</b>"
            )
        else:
            user_list = "\n".join(
                [
                    f"{idx + 1}. {user['fullname']} (@{user['username']}) - ID: {user['id']}"
                    for idx, user in enumerate(users)
                ]
            )
            await callback_query.message.answer(f"<b>📋 User List</b>\n\n{user_list}")
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to view the user list."
        )
    await callback_query.answer()
