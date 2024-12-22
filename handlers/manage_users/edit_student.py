from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states.user import UpdateStudent
from firebase.functions.users import get_user_data, update_user_data, get_users_in_class
from firebase.functions.classes import get_all_classes, get_class_data
from keyboards.inline.users import users_keyboard, edit_options_keyboard
from keyboards.inline.cancel import cancel_keyboard
from keyboards.inline.classes import classes_keyboard
from utils.main import delete_previous_message

route = "edit_student"
edit_student_router = Router()

cancel = cancel_keyboard(route)


@edit_student_router.callback_query(lambda c: c.data == route)
async def handle_edit_user(callback_query: CallbackQuery, state: FSMContext):
    """Entry point: Select a class."""
    classes = await get_all_classes()
    if not classes:
        await callback_query.answer("❌ No classes available.")
        return

    keyboard = await classes_keyboard(classes, route)
    classes_msg_id = await callback_query.message.answer(
        "<b>Select a class to edit its students:</b>", reply_markup=keyboard
    )
    await state.update_data(classes_msg_id=classes_msg_id.message_id)

    await callback_query.answer()


@edit_student_router.callback_query(lambda c: c.data.startswith(route))
async def handle_class_selection(callback_query: CallbackQuery, state: FSMContext):
    """Select a student from the chosen class."""
    class_id = callback_query.data.split("_")[2]
    students = await get_users_in_class(class_id)
    if not students:
        await callback_query.answer("❌ No students found in this class.")
        return

    keyboard = await users_keyboard(students, f"{route}_{class_id}")
    await callback_query.message.edit_text(
        "<b>Select a student to edit.</b>", reply_markup=keyboard
    )
    await state.update_data(selected_class=class_id)
    await callback_query.answer()


@edit_student_router.callback_query(lambda c: c.data.startswith("student_edit_student"))
async def handle_student_selection(callback: CallbackQuery, state: FSMContext):
    """Provide options for editing the selected student."""
    student_id = callback.data.split("_")[4]
    student_data = await get_user_data(student_id)

    if not student_data:
        await callback.answer("❌ Student not found.")
        return

    await state.update_data(student_id=student_id, student_data=student_data)

    keyboard = edit_options_keyboard(student_id)
    class_name = await get_class_data(student_data.get("class"))

    edit_user_options = await callback.message.edit_text(
        f"Full Name: {student_data.get('fullname', 'N/A')}\n"
        f"Username: {student_data.get('username', 'N/A')}\n"
        f"Class: {class_name['name']}\n",
        reply_markup=keyboard,
    )
    await state.update_data(edit_user_options_msg_id=edit_user_options.message_id)
    await callback.answer()


@edit_student_router.callback_query(lambda c: c.data.startswith("edit_fullname_"))
async def handle_edit_fullname(callback: CallbackQuery, state: FSMContext):
    """Prompt for a new full name."""
    student_id = callback.data.split("_")[2]
    await state.update_data(student_id=student_id)
    fullname_msg = await callback.message.answer(
        "<b>Please enter the new full name</b>", reply_markup=cancel
    )
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateStudent.fullname)
    await callback.answer()


@edit_student_router.callback_query(lambda c: c.data.startswith("edit_username_"))
async def handle_edit_username(callback: CallbackQuery, state: FSMContext):
    """Prompt for a new username."""
    student_id = callback.data.split("_")[2]
    await state.update_data(student_id=student_id)
    username_msg = await callback.message.answer(
        "<b>Please enter the new username</b>", reply_markup=cancel
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateStudent.username)
    await callback.answer()


@edit_student_router.callback_query(lambda c: c.data.startswith("change_class"))
async def handle_edit_class(callback: CallbackQuery, state: FSMContext):
    """Prompt to select a new class for the student."""
    student_id = callback.data.split("_")[2]
    classes = await get_all_classes()
    if not classes:
        await callback.answer("❌ No classes available.")
        return

    keyboard = await classes_keyboard(classes, f"set_change_class_{student_id}")
    username_msg = await callback.message.edit_text(
        "<b>Select a new class for the student.</b>", reply_markup=keyboard
    )
    await callback.answer()


@edit_student_router.message(UpdateStudent.fullname)
async def process_edit_fullname(message: Message, state: FSMContext):
    """Update the student's full name and delete the prompt message."""
    new_fullname = message.text
    data = await state.get_data()
    student_id = data["student_id"]

    await update_user_data(student_id, {"fullname": new_fullname})

    fullname_msg_id = data.get("fullname_msg_id")
    if fullname_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, fullname_msg_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Full name updated to: {new_fullname}")
    await state.clear()


@edit_student_router.message(UpdateStudent.username)
async def process_edit_username(message: Message, state: FSMContext):
    """Update the student's username and delete the prompt message."""
    new_username = message.text
    data = await state.get_data()
    student_id = data["student_id"]

    await update_user_data(student_id, {"username": new_username})

    username_msg_id = data.get("username_msg_id")
    if username_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, username_msg_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Username updated to: {new_username}")
    await state.clear()


@edit_student_router.callback_query(lambda c: c.data.startswith("set_change_class"))
async def process_change_class(callback: CallbackQuery):
    """Update the student's class."""
    _, _, _, student_id, new_class_id = callback.data.split("_")
    await update_user_data(student_id, {"class": new_class_id})

    await callback.answer("✅ Student's class has been updated.")


@edit_student_router.callback_query(
    lambda c: c.data.startswith("back_to_classes_edit_student")
)
async def back_to_classes_edit_student(callback: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    keyboard = await classes_keyboard(classes, route)
    select_class_msg = await callback.message.edit_text(
        "<b>Select a class to edit students</b>", reply_markup=keyboard
    )
    await state.update_data(select_class_msg_id=select_class_msg.message_id)

    await callback.answer()


@edit_student_router.callback_query(lambda c: c.data == "back_to_students")
async def back_to_students(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_id = data.get("selected_class")
    students = await get_users_in_class(class_id)
    student_keyboard = await users_keyboard(students, f"{route}_{class_id}")
    await callback.message.edit_text(
        "<b>Select a student to edit</b>", reply_markup=student_keyboard
    )
    await callback.answer()


@edit_student_router.callback_query(
    lambda c: c.data == "cancel_edit_student"
    or c.data.startswith("cancel_set_change_class")
)
async def cancel_edit_student(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids_to_delete = [
        data.get("fullname_msg_id"),
        data.get("user_id_msg_id"),
        data.get("username_msg_id"),
        data.get("classes_msg_id"),
        data.get("select_class_msg_id"),
    ]

    await callback.answer("❌ Student edition process has been canceled.")

    for msg_id in msg_ids_to_delete:
        await delete_previous_message(callback.message.chat.id, msg_id)

    await state.clear()
