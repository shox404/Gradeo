from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import DeleteTeacher
from firebase.functions.users import (
    delete_user_data,
    get_teachers_by_subject,
    get_teacher_data,
)
from firebase.functions.subjects import get_all_subjects
from keyboards.inline.users import teacher_keyboard,subject_keyboard, delete_teacher_confirmation_keyboard

delete_teacher_router = Router()


@delete_teacher_router.callback_query(lambda c: c.data == "delete_teacher")
async def delete_teacher_start(callback_query: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.message.answer("❌ No subjects found.")
        return
    keyboard = await subject_keyboard(subjects, "delete_teacher")
    await state.update_data(current_step="menu")
    await callback_query.message.answer(
        "<b>Select a subject to delete teachers</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@delete_teacher_router.callback_query(lambda c: c.data.startswith("subject_delete_teacher_"))
async def process_subject_selection(callback_query: CallbackQuery, state: FSMContext):
    subject_id = callback_query.data.split("_")[3]
    teachers = await get_teachers_by_subject(subject_id)
    if not teachers:
        await callback_query.message.answer("❌ No teachers found in this subject.")
        return
    keyboard = await teacher_keyboard(teachers, "delete")
    await state.update_data(current_step="subjects", selected_subject=subject_id)
    await callback_query.message.edit_text(
        "<b>Select a teacher to delete</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@delete_teacher_router.callback_query(lambda c: c.data.startswith("teacher_delete_"))
async def process_teacher_selection(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = callback_query.data.split("_")[2]
    teacher_data = await get_teacher_data(teacher_id)
    if not teacher_data:
        await callback_query.message.edit_text("❌ Teacher not found.")
        return
    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)
    confirm_teacher_delete_msg = await callback_query.message.edit_text(
        f"Are you sure you want to delete the teacher?\n"
        f"Name: {teacher_data['fullname']}\n"
        f"Username: @{teacher_data['username']}",
        reply_markup=delete_teacher_confirmation_keyboard,
    )
    await state.update_data(
        confirm_teacher_delete_msg_id=confirm_teacher_delete_msg.message_id
    )
    await state.set_state(DeleteTeacher.confirm_delete)
    await callback_query.answer()


@delete_teacher_router.callback_query(
    lambda c: c.data in ["confirm_teacher_delete_yes", "confirm_teacher_delete_no"]
)
async def confirm_delete_teacher(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    teacher_id = data.get("teacher_id")
    confirm_teacher_delete_msg_id = data.get("confirm_teacher_delete_msg_id")
    if confirm_teacher_delete_msg_id:
        await callback_query.bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=confirm_teacher_delete_msg_id,
        )

    if callback_query.data == "confirm_teacher_delete_yes":
        success = await delete_user_data(teacher_id)
        if success:
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=f"✅ Teacher with ID {teacher_id} has been deleted.",
            )
        else:
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Failed to delete teacher. Teacher may not exist.",
            )
    else:
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="❌ Teacher deletion canceled.",
        )

    await state.clear()
    await callback_query.answer()


@delete_teacher_router.callback_query(lambda c: c.data == "back_to_subjects")
async def back_to_subjects(callback_query: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    keyboard = await subject_keyboard(subjects, "delete")
    await callback_query.message.edit_text(
        "<b>Select a subject to delete teachers</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@delete_teacher_router.callback_query(lambda c: c.data == "back_to_teachers")
async def back_to_teachers(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("selected_subject")
    teachers = await get_teachers_by_subject(subject_id)
    keyboard = await teacher_keyboard(teachers, "delete")
    await callback_query.message.edit_text(
        "<b>Select a teacher to delete</b>", reply_markup=keyboard
    )
    await callback_query.answer()
