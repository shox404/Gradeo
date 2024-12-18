from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.mark import Mark
from firebase.functions.classes import get_all_classes
from firebase.functions.users import get_users_in_class, get_teacher_data
from firebase.functions.marks import get_marks_for_student, delete_mark
from firebase.functions.subjects import get_subject_by_id

delete_mark_router = Router()


@delete_mark_router.callback_query(lambda c: c.data == "delete_mark")
async def show_classes_for_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        classes = await get_all_classes()
        if not classes:
            await callback.message.edit_text("No classes found.")
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text=class_data["name"],
                    callback_data=f"estimate_delete_mark_{class_data['id']}",
                )
            ]
            for class_data in classes
        ]
        keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

        await callback.message.edit_text(
            text="Select a class for mark deletion:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
        await state.set_state(Mark.select_class)
    except Exception as e:
        await callback.message.edit_text(f"Error loading classes: {e}")


@delete_mark_router.callback_query(lambda c: c.data.startswith("estimate_delete_mark_"))
async def show_students_for_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        selected_class = callback.data.split("_")[3]
        await state.update_data(selected_class=selected_class)

        students = await get_users_in_class(selected_class)
        if not students:
            await callback.message.edit_text(
                f"No students found in the class '{selected_class}'."
            )
            return

        keyboard = [
            [
                InlineKeyboardButton(
                    text=student["fullname"],
                    callback_data=f"estimate_student_mark_{student['id']}",
                )
            ]
            for student in students
        ]
        keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

        await callback.message.edit_text(
            text=f"Select a student from '{selected_class}':",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
        await state.set_state(Mark.select_student)
    except Exception as e:
        await callback.message.edit_text(f"Error loading students: {e}")


@delete_mark_router.callback_query(lambda c: c.data.startswith("estimate_student_mark_"))
async def show_marks_for_deletion(callback: CallbackQuery, state: FSMContext):
    selected_student = callback.data.split("_")[3]
    await state.update_data(selected_student=selected_student)

    teacher_data = await get_teacher_data(callback.from_user.id)

    marks = await get_marks_for_student(selected_student, callback.from_user.id)
    if not marks:
        await callback.message.answer("No marks found for this student.")
        return

    keyboard = []
    for mark in marks:
        position = await get_subject_by_id(teacher_data["position"])
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{position['name']} - {mark['mark']}",
                    callback_data=f"confirm_delete_mark_{mark['id']}",
                )
            ]
        )
    keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

    await callback.message.edit_text(
        text="Select a mark to delete:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await state.set_state(Mark.select_mark)


@delete_mark_router.callback_query(lambda c: c.data.startswith("confirm_delete_mark_"))
async def confirm_mark_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        mark_id = callback.data.split("_")[3]
        await state.update_data(mark_id=mark_id)

        await callback.message.edit_text(
            text="Are you sure you want to delete this mark?",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="OK", callback_data="delete_mark_ok"),
                        InlineKeyboardButton(text="No", callback_data="cancel"),
                    ]
                ]
            ),
        )
        await state.set_state(Mark.confirm_deletion)
    except Exception as e:
        await callback.message.edit_text(f"Error during deletion confirmation: {e}")


@delete_mark_router.callback_query(lambda c: c.data == "delete_mark_ok")
async def handle_mark_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        mark_id = data.get("mark_id")

        await delete_mark(mark_id)
        await callback.message.edit_text(
            text="The mark has been successfully deleted.", reply_markup=None
        )
    except Exception as e:
        await callback.message.edit_text(f"Failed to delete the mark: {e}")

    await state.clear()


@delete_mark_router.callback_query(lambda c: c.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Operation cancelled.", reply_markup=None)
    await state.clear()
