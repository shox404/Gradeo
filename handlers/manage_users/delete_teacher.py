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
from keyboards.inline.users import (
    teacher_keyboard,
    subject_keyboard,
    delete_teacher_confirmation_keyboard,
)
from utils.main import delete_previous_message

delete_teacher_router = Router()


async def delete_messages_from_state(data, chat_id):
    msg_ids_to_delete = [
        data.get("confirm_teacher_delete_msg_id"),
    ]
    for msg_id in msg_ids_to_delete:
        if msg_id:
            await delete_previous_message(chat_id, msg_id)


@delete_teacher_router.callback_query(lambda c: c.data == "delete_teacher")
async def delete_teacher_start(callback: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    if not subjects:
        await callback.answer("❌ No subjects found.")
        return
    keyboard = await subject_keyboard(subjects, "delete_teacher")
    await state.update_data(current_step="menu")
    await callback.message.answer(
        "<b>Select a subject to delete teachers</b>", reply_markup=keyboard
    )
    await callback.answer()


@delete_teacher_router.callback_query(
    lambda c: c.data.startswith("delete_teacher_subject")
)
async def process_subject_selection(callback: CallbackQuery, state: FSMContext):
    subject_id = callback.data.split("_")[3]
    teachers = await get_teachers_by_subject(subject_id)
    if not teachers:
        await callback.answer("❌ No teachers found in this subject.")
        return
    keyboard = await teacher_keyboard(teachers, "delete_teacher")
    await state.update_data(current_step="subjects", selected_subject=subject_id)
    await callback.message.edit_text(
        "<b>Select a teacher to delete</b>", reply_markup=keyboard
    )
    await callback.answer()


@delete_teacher_router.callback_query(lambda c: c.data.startswith("teacher_delete_"))
async def process_teacher_selection(callback: CallbackQuery, state: FSMContext):
    teacher_id = callback.data.split("_")[3]
    teacher_data = await get_teacher_data(teacher_id)
    if not teacher_data:
        await callback.answer("❌ Teacher not found.")
        return
    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)
    confirm_teacher_delete_msg = await callback.message.edit_text(
        f"Are you sure you want to delete the teacher?\n"
        f"Name: {teacher_data['fullname']}\n"
        f"Username: {teacher_data['username']}",
        reply_markup=delete_teacher_confirmation_keyboard,
    )
    await state.update_data(
        confirm_teacher_delete_msg_id=confirm_teacher_delete_msg.message_id
    )
    await state.set_state(DeleteTeacher.confirm_delete)
    await callback.answer()


@delete_teacher_router.callback_query(lambda c: c.data == "confirm_teacher_delete_yes")
async def confirm_delete_teacher(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    teacher_id = data.get("teacher_id")
    confirm_teacher_delete_msg_id = data.get("confirm_teacher_delete_msg_id")

    if confirm_teacher_delete_msg_id:
        await delete_previous_message(
            callback.message.chat.id, confirm_teacher_delete_msg_id
        )

    success = await delete_user_data(teacher_id)
    if success:
        await callback.answer(f"✅ Teacher with ID {teacher_id} has been deleted.")
    else:
        await callback.answer("❌ Failed to delete teacher. Teacher may not exist.")

    await state.clear()


@delete_teacher_router.callback_query(lambda c: c.data == "back_to_subjects_delete_teacher")
async def back_to_subjects(callback_query: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    keyboard = await subject_keyboard(subjects, "delete_teacher")
    await callback_query.message.edit_text(
        "<b>Select a subject to delete teachers.</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@delete_teacher_router.callback_query(lambda c: c.data == "back_to_teachers")
async def back_to_teachers(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("selected_subject")
    teachers = await get_teachers_by_subject(subject_id)
    keyboard = await teacher_keyboard(teachers, "delete_teacher")
    await callback.message.edit_text(
        "<b>Select a teacher to delete.</b>", reply_markup=keyboard
    )
    await callback.answer()


@delete_teacher_router.callback_query(
    lambda c: c.data == "cancel_delete_teacher"
    or c.data == "cancel_select_subject_delete_teacher"
)
async def cancel_teacher_process(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer("❌ Teacher deletion canceled.")

    await delete_messages_from_state(data, callback.message.chat.id)

    await state.clear()
