from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from states.user import UpdateUser
from firebase.functions.users import get_user_data, update_user_data, get_users_in_class
from firebase.functions.classes import get_all_classes, get_class_data

edit_user_router = Router()


def class_keyboard(classes) -> InlineKeyboardMarkup:
    """Keyboard to select a class."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=cls["name"], callback_data=f"select_class_{cls['id']}"
                )
            ]
            for cls in classes
        ]
    )


def user_keyboard(users, class_id: str) -> InlineKeyboardMarkup:
    """Keyboard to select a student."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=user["fullname"],
                    callback_data=f"select_student_{class_id}_{user['id']}",
                )
            ]
            for user in users
        ]
    )


def edit_options_keyboard(student_id: str) -> InlineKeyboardMarkup:
    """Keyboard to select an edit option for a student."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Edit Full Name", callback_data=f"edit_fullname_{student_id}"
                ),
                InlineKeyboardButton(
                    text="✏️ Edit Username", callback_data=f"edit_username_{student_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Change Class", callback_data=f"edit_class_{student_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Students", callback_data="back_to_students"
                )
            ],
        ]
    )


def class_selection_keyboard(classes, student_id: str) -> InlineKeyboardMarkup:
    """Keyboard to select a new class for the student."""
    buttons = [
        [
            InlineKeyboardButton(
                text=cls["name"], callback_data=f"change_class_{student_id}_{cls['id']}"
            )
        ]
        for cls in classes
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Back to Edit Options",
                callback_data=f"back_to_edit_{student_id}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@edit_user_router.callback_query(lambda c: c.data == "edit_user")
async def handle_edit_user(callback_query: CallbackQuery):
    """Entry point_ Select a class."""
    classes = await get_all_classes()
    if not classes:
        await callback_query.message.answer("❌ No classes available.")
        return

    keyboard = class_keyboard(classes)
    await callback_query.message.answer(
        "<b>Select a class to edit its students:</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("select_class_"))
async def handle_class_selection(callback_query: CallbackQuery, state: FSMContext):
    """Select a student from the chosen class."""
    class_id = callback_query.data.split("_")[2]
    students = await get_users_in_class(class_id)
    if not students:
        await callback_query.message.edit_text("❌ No students found in this class.")
        return

    keyboard = user_keyboard(students, class_id)
    await callback_query.message.edit_text(
        "<b>Select a student to edit_</b>", reply_markup=keyboard
    )
    await state.update_data(selected_class=class_id)
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("select_student_"))
async def handle_student_selection(callback_query: CallbackQuery, state: FSMContext):
    """Provide options for editing the selected student."""
    _, _, _, student_id = callback_query.data.split("_")
    student_data = await get_user_data(student_id)

    if not student_data:
        await callback_query.message.edit_text("❌ Student not found.")
        return

    await state.update_data(student_id=student_id, student_data=student_data)

    keyboard = edit_options_keyboard(student_id)
    class_name = await get_class_data(student_data.get("class"))

    edit_user_options = await callback_query.message.edit_text(
        f"Full Name: {student_data.get('fullname', 'N/A')}\n"
        f"Username: @{student_data.get('username', 'N/A')}\n"
        f"Class: {class_name["name"]}\n",
        reply_markup=keyboard,
    )
    await state.update_data(edit_user_options_msg_id=edit_user_options.message_id)
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("edit_fullname_"))
async def handle_edit_fullname(callback_query: CallbackQuery, state: FSMContext):
    """Prompt for a new full name."""
    student_id = callback_query.data.split("_")[2]
    await state.update_data(student_id=student_id)
    fullname_msg = await callback_query.message.answer(
        "<b>Please enter the new full name</b>"
    )
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateUser.fullname)
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("edit_username_"))
async def handle_edit_username(callback_query: CallbackQuery, state: FSMContext):
    """Prompt for a new username."""
    student_id = callback_query.data.split("_")[2]
    await state.update_data(student_id=student_id)
    username_msg = await callback_query.message.answer(
        "<b>Please enter the new username</b>"
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateUser.username)
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("edit_class_"))
async def handle_edit_class(callback_query: CallbackQuery, state: FSMContext):
    """Prompt to select a new class for the student."""
    student_id = callback_query.data.split("_")[2]
    classes = await get_all_classes()
    if not classes:
        await callback_query.message.answer("❌ No classes available.")
        return

    keyboard = class_selection_keyboard(classes, student_id)
    await callback_query.message.edit_text(
        "<b>Select a new class for the student.</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@edit_user_router.message(UpdateUser.fullname)
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
    edit_user_options_msg_id = data.get("edit_user_options_msg_id")
    if edit_user_options_msg_id:
        try:
            await message.bot.delete_message(
                message.from_user.id, edit_user_options_msg_id
            )
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Full name updated to: {new_fullname}")
    await state.clear()


@edit_user_router.message(UpdateUser.username)
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
    edit_user_options_msg_id = data.get("edit_user_options_msg_id")
    if edit_user_options_msg_id:
        try:
            await message.bot.delete_message(
                message.from_user.id, edit_user_options_msg_id
            )
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Username updated to: @{new_username}")
    await state.clear()


@edit_user_router.callback_query(lambda c: c.data.startswith("change_class_"))
async def process_change_class(callback_query: CallbackQuery):
    """Update the student's class."""
    _, _, student_id, new_class_id = callback_query.data.split("_")
    await update_user_data(student_id, {"class": new_class_id})

    await callback_query.message.edit_text("✅ Student's class has been updated.")
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data == "back_to_students")
async def back_to_students(callback_query: CallbackQuery, state: FSMContext):
    """Go back to the student list."""
    data = await state.get_data()
    class_id = data.get("selected_class")
    students = await get_users_in_class(class_id)

    if not students:
        await callback_query.message.edit_text("❌ No students found.")
        return

    keyboard = user_keyboard(students, class_id)
    await callback_query.message.edit_text(
        "<b>Select a student to edit_</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("back_to_edit_"))
async def back_to_edit_options(callback_query: CallbackQuery, state: FSMContext):
    """Go back to the edit options after changing the class."""
    student_id = callback_query.data.split("_")[2]
    student_data = await get_user_data(student_id)

    if not student_data:
        await callback_query.message.edit_text("❌ Student not found.")
        return

    await state.update_data(student_id=student_id, student_data=student_data)

    keyboard = edit_options_keyboard(student_id)
    class_name = await get_class_data(student_data.get("class"))

    await callback_query.message.edit_text(
        f"Full Name: {student_data.get('fullname', 'N/A')}\n"
        f"Username: @{student_data.get('username', 'N/A')}\n"
        f"Class: {class_name}\n",
        reply_markup=keyboard,
    )
    await callback_query.answer()
