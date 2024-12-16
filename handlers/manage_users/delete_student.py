from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import DeleteUser
from utils.detect_admin import is_admin
from firebase.functions.users import delete_user_data, get_users_in_class, get_user_data
from firebase.functions.classes import get_all_classes
from keyboards.inline.users import (
    class_keyboard,
    user_keyboard,
    delete_confirmation_keyboard,
)

delete_student_router = Router()


@delete_student_router.callback_query(lambda c: c.data == "delete_student")
async def delete_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        classes = await get_all_classes()
        if not classes:
            await callback_query.message.answer("❌ No classes found.")
            return
        keyboard = await class_keyboard(classes, "delete")
        await state.update_data(current_step="menu")
        await callback_query.message.answer(
            "<b>Select a class to delete students</b>", reply_markup=keyboard
        )
    await callback_query.answer()


@delete_student_router.callback_query(lambda c: c.data.startswith("class_delete_"))
async def process_class_selection(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        class_id = callback_query.data.split("_")[2]
        students = await get_users_in_class(class_id)
        if not students:
            await callback_query.message.answer("❌ No students found in this class.")
            return
        student_keyboard = await user_keyboard(students, "delete")
        await state.update_data(current_step="classes", selected_class=class_id)
        await callback_query.message.edit_text(
            "<b>Select a student to delete</b>", reply_markup=student_keyboard
        )
    await callback_query.answer()


@delete_student_router.callback_query(lambda c: c.data.startswith("student_delete_"))
async def process_student_selection(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        student_id = callback_query.data.split("_")[2]
        user_data = await get_user_data(student_id)
        if not user_data:
            await callback_query.message.edit_text("❌ No student found with this ID.")
            return
        await state.update_data(student_id=student_id, user_data=user_data)
        confirm_user_delete_msg = await callback_query.message.edit_text(
            f"Are you sure you want to delete the user with ID {student_id}?\n"
            f"Name: {user_data['fullname']}\n"
            f"Username: @{user_data['username']}",
            reply_markup=delete_confirmation_keyboard,
        )
        await state.update_data(
            confirm_user_delete_msg_id=confirm_user_delete_msg.message_id
        )
        await state.set_state(DeleteUser.confirm_delete)
    await callback_query.answer()


@delete_student_router.callback_query(
    lambda c: c.data in ["confirm_user_delete_yes", "confirm_user_delete_no"]
)
async def confirm_delete_user(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        data = await state.get_data()
        student_id = data.get("student_id")
        confirm_user_delete_msg_id = data.get("confirm_user_delete_msg_id")

        if confirm_user_delete_msg_id:
            await callback_query.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=confirm_user_delete_msg_id,
            )

        if callback_query.data == "confirm_user_delete_yes":
            success = await delete_user_data(student_id)
            if success:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=f"✅ User with ID {student_id} has been deleted.",
                )
            else:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="❌ Failed to delete user. User may not exist.",
                )
        else:
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ User deletion canceled.",
            )

        await state.clear()
    await callback_query.answer()


@delete_student_router.callback_query(lambda c: c.data == "back_to_classes")
async def back_to_classes(callback_query: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    keyboard = await class_keyboard(classes, "delete")
    await callback_query.message.edit_text(
        "<b>Select a class to delete students</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@delete_student_router.callback_query(lambda c: c.data == "back_to_students")
async def back_to_students(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_id = data.get("selected_class")
    students = await get_users_in_class(class_id)
    student_keyboard = await user_keyboard(students, "delete")
    await callback_query.message.edit_text(
        "<b>Select a student to delete</b>", reply_markup=student_keyboard
    )
    await callback_query.answer()
