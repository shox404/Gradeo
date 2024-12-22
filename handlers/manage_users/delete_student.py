from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import DeleteUser
from utils.detect_admin import is_admin
from firebase.functions.users import delete_user_data, get_users_in_class, get_user_data
from firebase.functions.classes import get_all_classes
from keyboards.inline.users import users_keyboard, delete_confirmation_keyboard
from keyboards.inline.classes import classes_keyboard
from utils.main import delete_previous_message

delete_student_router = Router()


@delete_student_router.callback_query(lambda c: c.data == "delete_student")
async def delete_user_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        classes = await get_all_classes()
        if not classes:
            await callback.message.answer("❌ No classes found.")
            return
        keyboard = await classes_keyboard(classes, "select_class_delete_user")
        await state.update_data(current_step="menu")
        classes_first_msg = await callback.message.answer(
            "<b>Select a class to delete students</b>", reply_markup=keyboard
        )
        await state.update_data(classes_first_msg_id=classes_first_msg.message_id)
    await callback.answer()


@delete_student_router.callback_query(
    lambda c: c.data.startswith("select_class_delete_user")
)
async def process_class_selection(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        class_id = callback.data.split("_")[4]
        students = await get_users_in_class(class_id)
        if not students:
            await callback.answer("❌ No students found in this class.")
            return
        student_keyboard = await users_keyboard(students, "delete_student")
        await state.update_data(current_step="classes", selected_class=class_id)
        await callback.message.edit_text(
            "<b>Select a student to delete</b>", reply_markup=student_keyboard
        )
    await callback.answer()


@delete_student_router.callback_query(
    lambda c: c.data.startswith("student_delete_student")
)
async def process_student_selection(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        student_id = callback.data.split("_")[3]
        user_data = await get_user_data(student_id)
        if not user_data:
            await callback.answer("❌ No student found with this ID.")
            return
        await state.update_data(student_id=student_id, user_data=user_data)
        confirm_user_delete_msg = await callback.message.edit_text(
            f"Are you sure you want to delete the user with ID {student_id}?\n"
            f"Name: {user_data['fullname']}\n"
            f"Username: {user_data['username']}",
            reply_markup=delete_confirmation_keyboard,
        )
        await state.update_data(
            confirm_user_delete_msg_id=confirm_user_delete_msg.message_id
        )
        await state.set_state(DeleteUser.confirm_delete)
    await callback.answer()


@delete_student_router.callback_query(lambda c: c.data == "confirm_user_delete_yes")
async def confirm_delete_user(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        data = await state.get_data()
        student_id = data.get("student_id")
        confirm_user_delete_msg_id = data.get("confirm_user_delete_msg_id")

        if callback.data == "confirm_user_delete_yes":
            success = await delete_user_data(student_id)
            if success:
                await callback.answer(f"✅ User with ID {student_id} has been deleted.")
            else:
                await callback.answer("❌ Failed to delete user. User may not exist.")

        if confirm_user_delete_msg_id:
            await delete_previous_message(
                callback.message.chat.id, confirm_user_delete_msg_id
            )

        await state.clear()
    await callback.answer()


@delete_student_router.callback_query(
    lambda c: c.data.startswith("back_to_classes_delete_student")
)
async def back_to_classes_delete(callback: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    keyboard = await classes_keyboard(classes, "select_class_delete_user")
    classes_second_msg = await callback.message.edit_text(
        "<b>Select a class to delete students</b>", reply_markup=keyboard
    )
    await state.update_data(classes_sencond_msg_id=classes_second_msg.message_id)
    await callback.answer()


@delete_student_router.callback_query(lambda c: c.data == "back_to_students_delete")
async def back_to_students_delete(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_id = data.get("selected_class")
    students = await get_users_in_class(class_id)
    student_keyboard = await users_keyboard(students, "delete")
    await callback.message.edit_text(
        "<b>Select a student to delete</b>", reply_markup=student_keyboard
    )
    await callback.answer()


@delete_student_router.callback_query(
    lambda c: c.data == "cancel_delete_student"
    or c.data == "cancel_select_class_delete_user"
)
async def cancel_edit_student(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids_to_delete = [
        data.get("current_step"),
        data.get("selected_class"),
        data.get("classes_first_msg_id"),
        data.get("classes_sencond_msg_id"),
    ]

    await callback.answer("❌ User deletion canceled.")

    for msg_id in msg_ids_to_delete:
        await delete_previous_message(callback.message.chat.id, msg_id)

    await state.clear()
