from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import User
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions.users import save_user_data
from firebase.functions.classes import get_all_classes, get_class_data
from firebase.functions.subjects import get_subject_by_id
from keyboards.inline.classes import classes_keyboard
from keyboards.inline.users import cancel_keyboard, subjects_keyboard

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
        error_msg_id = data.get("error_msg_id")
        if error_msg_id:
            await message.bot.delete_message(message.chat.id, error_msg_id)
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
    role_msg_id = data.get("role_msg_id")
    if role_msg_id:
        await message.bot.delete_message(message.chat.id, role_msg_id)
    await message.delete()

    role = message.text
    await state.update_data(role=role)

    if role == "Student":
        classes = await get_all_classes()
        class_keyboard = await classes_keyboard(classes, "add_user")
        class_msg = await message.answer(
            "<b>Please select the class of the student.</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(class_msg_id=class_msg.message_id)
        await state.set_state(User.student_class)

    elif role == "Teacher":
        subject_keyboard = await subjects_keyboard()
        subject_msg = await message.answer(
            "<b>Please select the teacher's subject.</b>",
            reply_markup=subject_keyboard,
        )
        await state.update_data(subject_msg_id=subject_msg.message_id)
        await state.set_state(User.position)  
        

@add_user_router.callback_query(lambda c: c.data.startswith("subject_add_"))
async def process_subject(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "Cancel":
        await state.clear()
        await callback_query.message.answer("User creation process has been canceled.")
        await callback_query.answer()
        return

    data = await state.get_data()
    subject_msg_id = data.get("subject_msg_id")
    if subject_msg_id:
        await callback_query.bot.delete_message(
            callback_query.message.chat.id, subject_msg_id
        )

    subject = callback_query.data[8:]
    await state.update_data(position=subject)
    await finalize_user_data(callback_query, state)
    await callback_query.answer()


@add_user_router.callback_query(lambda c: str(c.data).startswith("class_add_user"))
async def process_user_class(callback_query: CallbackQuery, state: FSMContext):
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
    await state.update_data(user_class=class_id)
    await finalize_user_data(callback_query, state)


@add_user_router.callback_query(lambda c: c.data == "cancel_add_user")
async def cancel_add_user(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids_to_delete = [
        data.get("fullname_msg_id"),
        data.get("user_id_msg_id"),
        data.get("username_msg_id"),
        data.get("role_msg_id"),
        data.get("class_msg_id"),
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


async def finalize_user_data(
    message_or_callback: Message | CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    fullname = data.get("fullname")
    user_id = data.get("user_id")
    username = data.get("username")
    role = data.get("role")

    position = data.get("position") if role == "Teacher" else None
    class_id = data.get("user_class") if role == "Student" else None
    user_class = await get_class_data(class_id) if class_id else None
    user_position = await get_subject_by_id(position[4::]) if position else None

    info_message = (
        f"<b>New {role} added</b>\n"
        f"👤 <b>Name:</b> {fullname}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"🌐 <b>Username:</b> {username}\n"
    )
    if role == "Teacher" and position:
        info_message += f"📌 <b>Position:</b> {user_position['name']}\n"
    if role == "Student" and user_class:
        info_message += f"🏫 <b>Class:</b> {user_class['name']}\n"

    if isinstance(message_or_callback, Message):
        await message_or_callback.answer(info_message)
    elif isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.answer(info_message)

    user_data = {
        "fullname": fullname,
        "user_id": user_id,
        "username": username,
        "role": role,
    }
    if role == "Teacher" and position:
        user_data["position"] = position[4::]
    if role == "Student" and user_class:
        user_data["class"] = user_class["id"]

    await save_user_data(user_data)
    await state.clear()
