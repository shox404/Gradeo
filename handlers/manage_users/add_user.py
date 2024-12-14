from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import User
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions.users import save_user_data
from firebase.functions.classes import get_all_classes, get_class_data
from keyboards.inline.classes import classes_keyboard
from keyboards.inline.users import cancel_keyboard

add_user_router = Router()


@add_user_router.callback_query(lambda c: c.data == "add_user")
async def add_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        fullname_msg = await callback_query.message.answer(
            "<b>Please enter the full name.</b>", reply_markup=cancel_keyboard
        )
        await state.update_data(fullname_msg_id=fullname_msg.message_id)
        await state.set_state(User.fullname)
    else:
        await callback_query.message.answer(
            "⛔ Sizda ushbu buyruqdan foydalanish huquqi yo'q."
        )
    await callback_query.answer()


@add_user_router.message(User.fullname)
async def process_fullname(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("User creation process has been canceled.")
        return
    data = await state.get_data()
    fullname_msg_id = data.get("fullname_msg_id")
    if fullname_msg_id:
        await message.bot.delete_message(message.chat.id, fullname_msg_id)
    await message.delete()
    await state.update_data(fullname=message.text)
    user_id_msg = await message.answer(
        "<b>Please enter the user ID of the new user.</b>", reply_markup=cancel_keyboard
    )
    await state.update_data(user_id_msg_id=user_id_msg.message_id)
    await state.set_state(User.user_id)


@add_user_router.message(User.user_id)
async def process_user_id(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("User creation process has been canceled.")
        return
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
        "<b>Please enter the username of the new user.</b>",
        reply_markup=cancel_keyboard,
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(User.username)


@add_user_router.message(User.username)
async def process_username(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("User creation process has been canceled.")
        return
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


@add_user_router.message(lambda m: m.text in ["Teacher", "Student"])
async def process_role_message(message: Message, state: FSMContext):
    if message.text == "Cancel":
        await state.clear()
        await message.answer("User creation process has been canceled.")
        return
    data = await state.get_data()
    classes = await get_all_classes()
    role_msg_id = data.get("role_msg_id")
    if role_msg_id:
        await message.bot.delete_message(message.chat.id, role_msg_id)
    await message.delete()
    role = message.text
    await state.update_data(role=role)
    if role == "Student":
        class_keyboard = await classes_keyboard(classes, "add_user")
        class_msg = await message.answer(
            "<b>Please select the class of the student.</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(class_msg_id=class_msg.message_id)
        await state.set_state(User.student_class)
    else:
        await finalize_user_data(message, state)


@add_user_router.callback_query(lambda c: str(c.data).startswith("class_add_user"))
async def process_student_class(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "Cancel":
        await state.clear()
        await callback_query.message.answer("User creation process has been canceled.")
        return
    data = await state.get_data()
    class_msg_id = data.get("class_msg_id")
    if class_msg_id:
        await callback_query.bot.delete_message(
            callback_query.message.chat.id, class_msg_id
        )
    class_id = callback_query.data[15::]
    await state.update_data(student_class=class_id)
    await finalize_user_data(callback_query, state)


async def finalize_user_data(
    message_or_callback: Message | CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    fullname = data.get("fullname")
    user_id = data.get("user_id")
    username = data.get("username")
    role = data.get("role")
    class_id = data.get("student_class") if role == "Student" else None
    student_class = await get_class_data(class_id)
    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(
            f"<b>New {role} added</b>\n"
            f"👤 <b>Name:</b> {fullname}\n"
            f"🆔 <b>ID:</b> {user_id}\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"🏫 <b>Class:</b> {student_class['name']}"
        )
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(
            f"<b>New {role} added</b>\n"
            f"👤 <b>Name:</b> {fullname}\n"
            f"🆔 <b>ID:</b> {user_id}\n"
            f"🌐 <b>Username:</b> {username}\n"
            f"🏫 <b>Class:</b> {student_class['name']}"
        )
    user_data = {
        "fullname": fullname,
        "user_id": user_id,
        "username": username,
        "role": role,
        "class": student_class['id'],
    }
    await save_user_data(user_data)
    await state.clear()


@add_user_router.callback_query(lambda c: c.data == "cancel_add_user")
async def cancel_add_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    fullname_msg_id = data.get("fullname_msg_id")
    user_id_msg_id = data.get("user_id_msg_id")
    username_msg_id = data.get("username_msg_id")
    role_msg_id = data.get("role_msg_id")
    class_msg_id = data.get("class_msg_id")

    msg_ids_to_delete = [
        fullname_msg_id,
        user_id_msg_id,
        username_msg_id,
        role_msg_id,
        class_msg_id,
    ]

    for msg_id in msg_ids_to_delete:
        if msg_id:
            try:
                await callback_query.message.bot.delete_message(
                    callback_query.message.chat.id, msg_id
                )
            except Exception as e:
                print(f"Failed to delete message with ID {msg_id}: {e}")

    await state.clear()
    await callback_query.message.answer("User creation process has been canceled.")
    await callback_query.answer()
