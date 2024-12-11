from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from states.user import User
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions import save_user_data

add_user_router = Router()


@add_user_router.message(Command("add_user"))
async def add_user_start(message: Message, state: FSMContext):
    if await is_admin(message):
        fullname_msg = await message.answer("<b>Please enter the full name.</b>")
        await state.update_data(fullname_msg_id=fullname_msg.message_id)
        await state.set_state(User.fullname)
    else:
        await message.answer("⛔ Sizda ushbu buyruqdan foydalanish huquqi yo'q.")


@add_user_router.message(User.fullname)
async def process_fullname(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        fullname_msg_id = data.get("fullname_msg_id")
        if fullname_msg_id:
            await message.bot.delete_message(message.chat.id, fullname_msg_id)
        await message.delete()
        await state.update_data(fullname=message.text)
        user_id_msg = await message.answer(
            "<b>Please enter the user ID of the new user.</b>"
        )
        await state.update_data(user_id_msg_id=user_id_msg.message_id)
        await state.set_state(User.user_id)


@add_user_router.message(User.user_id)
async def process_user_id(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        user_id_msg_id = data.get("user_id_msg_id")
        if user_id_msg_id:
            await message.bot.delete_message(message.chat.id, user_id_msg_id)
        await message.delete()
        try:
            user_id = int(message.text)
            await state.update_data(user_id=user_id)
        except ValueError:
            error_msg = await message.answer(
                "❌ Invalid user ID. Please enter a valid numeric user ID."
            )
            await state.update_data(error_msg_id=error_msg.message_id)
            return
        username_msg = await message.answer(
            "<b>Please enter the username of the new user.</b>"
        )
        await state.update_data(username_msg_id=username_msg.message_id)
        await state.set_state(User.username)


@add_user_router.message(User.username)
async def process_username(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        username_msg_id = data.get("username_msg_id")
        if username_msg_id:
            await message.bot.delete_message(message.chat.id, username_msg_id)
        await message.delete()
        username = message.text
        await state.update_data(username=username)
        role_msg = await message.answer(
            "<b>Now, select the role for the new user.</b>", reply_markup=role_keyboard
        )
        await state.update_data(role_msg_id=role_msg.message_id)
        await state.set_state(User.role)


@add_user_router.message(User.role)
async def process_role(message: Message, state: FSMContext):
    if await is_admin(message):
        if message.text not in ["Teacher", "Student"]:
            await message.answer(
                "❌ Invalid role! Please select either 'Teacher' or 'Student'.",
                reply_markup=role_keyboard,
            )
            return

        await state.update_data(role=message.text)

        data = await state.get_data()
        role = data.get("role")

        if not role:
            await message.answer(
                "❌ Role is not set. Please try again.", reply_markup=role_keyboard
            )
            return

        role_msg_id = data.get("role_msg_id")
        if role_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=role_msg_id
            )

        fullname = data.get("fullname")
        user_id = data.get("user_id")
        username = (
            f"@{data.get('username')}"
            if "@" not in data.get("username")
            else data.get("username")
        )

        await message.answer(
            f"<b>New user added:</b>\n"
            f"👤 <b>Name:</b> {fullname}\n"
            f"🆔 <b>ID:</b> {user_id}\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"📘 <b>Role:</b> {role}"
        )

        await save_user_data(
            {
                "fullname": fullname,
                "user_id": user_id,
                "username": username,
                "role": role,
            }
        )

        await state.clear()
