from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from states.user import UpdateTeacher
from firebase.functions.users import get_teacher_data, update_teacher_data, get_teachers_by_subject
from firebase.functions.subjects import get_all_subjects

edit_teacher_router = Router()

def subject_keyboard(subjects) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=subj["name"], callback_data=f"select_subject_{subj['id']}"
                )
            ]
            for subj in subjects
        ]
    )

def teacher_keyboard(teachers, subject_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=teacher["fullname"],
                    callback_data=f"select_teacher_{subject_id}_{teacher['id']}",
                )
            ]
            for teacher in teachers
        ]
    )

def edit_teacher_options_keyboard(teacher_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Edit Full Name", callback_data=f"edit_fullname_{teacher_id}"
                ),
                InlineKeyboardButton(
                    text="✏️ Edit Username", callback_data=f"edit_username_{teacher_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Edit Position (Subject)", callback_data=f"edit_position_{teacher_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back to Teachers", callback_data="back_to_teachers"
                )
            ],
        ]
    )

def position_selection_keyboard(subjects, teacher_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=subj["name"], callback_data=f"change_position_{teacher_id}_{subj['id']}"
            )
        ]
        for subj in subjects
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Back to Edit Options",
                callback_data=f"back_to_edit_{teacher_id}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@edit_teacher_router.callback_query(lambda c: c.data == "edit_teacher")
async def handle_edit_teacher(callback_query: CallbackQuery):
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.message.answer("❌ No subjects available.")
        return

    keyboard = subject_keyboard(subjects)
    await callback_query.message.answer(
        "<b>Select a subject to edit its teachers:</b>", reply_markup=keyboard
    )
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("select_subject_"))
async def handle_subject_selection(callback_query: CallbackQuery, state: FSMContext):
    subject_id = callback_query.data.split("_")[2]
    teachers = await get_teachers_by_subject(subject_id)
    if not teachers:
        await callback_query.answer("❌ No teachers found for this subject.")
        return

    keyboard = teacher_keyboard(teachers, subject_id)
    await callback_query.message.edit_text(
        "<b>Select a teacher to edit</b>", reply_markup=keyboard
    )
    await state.update_data(selected_subject=subject_id)
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("select_teacher_"))
async def handle_teacher_selection(callback_query: CallbackQuery, state: FSMContext):
    _, _, _, teacher_id = callback_query.data.split("_")
    teacher_data = await get_teacher_data(teacher_id)

    if not teacher_data:
        await callback_query.message.edit_text("❌ Teacher not found.")
        return

    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)

    keyboard = edit_teacher_options_keyboard(teacher_id)
    await callback_query.message.edit_text(
        f"Full Name: {teacher_data.get('fullname', 'N/A')}\n"
        f"Username: @{teacher_data.get('username', 'N/A')}\n"
        f"Position: {teacher_data.get('position', 'N/A')}\n",
        reply_markup=keyboard,
    )
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_fullname_"))
async def handle_edit_teacher_fullname(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = callback_query.data.split("_")[2]
    await state.update_data(teacher_id=teacher_id)
    fullname_msg = await callback_query.message.answer(
        "<b>Please enter the new full name</b>"
    )
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateTeacher.fullname)
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_username_"))
async def handle_edit_teacher_username(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = callback_query.data.split("_")[2]
    await state.update_data(teacher_id=teacher_id)
    username_msg = await callback_query.message.answer(
        "<b>Please enter the new username</b>"
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateTeacher.username)
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_position_"))
async def handle_edit_teacher_position(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = callback_query.data.split("_")[2]
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.message.answer("❌ No subjects available.")
        return

    keyboard = position_selection_keyboard(subjects, teacher_id)
    await callback_query.message.edit_text(
        "<b>Select a new position (subject) for the teacher:</b>", reply_markup=keyboard
    )
    await callback_query.answer()

@edit_teacher_router.message(UpdateTeacher.fullname)
async def process_edit_teacher_fullname(message: Message, state: FSMContext):
    new_fullname = message.text
    data = await state.get_data()
    teacher_id = data["teacher_id"]

    await update_teacher_data(teacher_id, {"fullname": new_fullname})

    fullname_msg_id = data.get("fullname_msg_id")
    if fullname_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, fullname_msg_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Full name updated to: {new_fullname}")
    await state.clear()

@edit_teacher_router.message(UpdateTeacher.username)
async def process_edit_teacher_username(message: Message, state: FSMContext):
    new_username = message.text
    data = await state.get_data()
    teacher_id = data["teacher_id"]

    await update_teacher_data(teacher_id, {"username": new_username})

    username_msg_id = data.get("username_msg_id")
    if username_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, username_msg_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    await message.delete()

    await message.answer(f"✅ Username updated to: @{new_username}")
    await state.clear()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("change_position_"))
async def process_change_teacher_position(callback_query: CallbackQuery):
    _, _, teacher_id, new_subject_id = callback_query.data.split("_")
    await update_teacher_data(teacher_id, {"position": new_subject_id})

    await callback_query.message.edit_text("✅ Teacher's position has been updated.")
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data == "back_to_teachers")
async def back_to_teachers(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("selected_subject")
    teachers = await get_teachers_by_subject(subject_id)

    if not teachers:
        await callback_query.message.edit_text("❌ No teachers found.")
        return

    keyboard = teacher_keyboard(teachers, subject_id)
    await callback_query.message.edit_text(
        "<b>Select a teacher to edit:</b>", reply_markup=keyboard
    )
    await callback_query.answer()

@edit_teacher_router.callback_query(lambda c: c.data.startswith("back_to_edit_"))
async def back_to_teacher_edit_options(callback_query: CallbackQuery, state: FSMContext):
    teacher_id = callback_query.data.split("_")[2]
    teacher_data = await get_teacher_data(teacher_id)

    if not teacher_data:
        await callback_query.message.edit_text("❌ Teacher not found.")
        return

    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)

    keyboard = edit_teacher_options_keyboard(teacher_id)
    await callback_query.message.edit_text(
        f"Full Name: {teacher_data.get('fullname', 'N/A')}\n"
        f"Username: @{teacher_data.get('username', 'N/A')}\n"
        f"Position: {teacher_data.get('position', 'N/A')}\n",
        reply_markup=keyboard,
    )
    await callback_query.answer()
