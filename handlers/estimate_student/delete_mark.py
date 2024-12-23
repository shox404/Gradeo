from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.mark import Mark
from firebase.functions.classes import get_all_classes
from firebase.functions.users import get_users_in_class, get_teacher_data
from firebase.functions.marks import get_marks_for_student, delete_mark
from firebase.functions.subjects import get_subject_by_id
from keyboards.inline.classes import classes_keyboard
from keyboards.inline.users import users_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

route = "delete_mark"
delete_mark_router = Router()


def students_keyboard(students, callback_prefix: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=student["fullname"],
                callback_data=f"{callback_prefix}_student_{student['id']}",
            )
        ]
        for student in students
    ]
    keyboard.append(
        [InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{callback_prefix}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def marks_keyboard(marks, callback_prefix: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"{mark['subject']} - {mark['mark']}",
                callback_data=f"{callback_prefix}_mark_{mark['id']}",
            )
        ]
        for mark in marks
    ]
    keyboard.append(
        [InlineKeyboardButton(text="Cancel", callback_data=f"cancel_{callback_prefix}")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_keyboard(callback_prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Yes", callback_data=f"{callback_prefix}_yes"
                ),
                InlineKeyboardButton(
                    text="No", callback_data=f"cancel_{callback_prefix}"
                ),
            ]
        ]
    )


@delete_mark_router.callback_query(lambda c: c.data == "delete_mark")
async def show_classes_for_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        classes = await get_all_classes()
        if not classes:
            await callback.answer("❌ No classes found.")
            return

        keyboard = await classes_keyboard(classes, "delete_student_mark")
        await callback.message.answer(
            text="Select a class for mark deletion:", reply_markup=keyboard
        )
        await state.set_state(Mark.select_class)
    except Exception as e:
        await callback.answer(f"❌ Error loading classes: {e}")
    await callback.answer()


@delete_mark_router.callback_query(lambda c: c.data.startswith("delete_student_mark"))
async def show_students_for_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        selected_class = callback.data.split("_")[3]
        await state.update_data(selected_class=selected_class)

        students = await get_users_in_class(selected_class)
        if not students:
            await callback.answer("❌ No students found in this class.")
            return

        keyboard = await users_keyboard(students, "select_student_marks")
        await callback.message.edit_text(
            text="Select a student:", reply_markup=keyboard
        )
        await state.set_state(Mark.select_student)
    except Exception as e:
        await callback.answer(f"❌ Error loading students: {e}")


@delete_mark_router.callback_query(lambda c: c.data.startswith("select_student_marks"))
async def show_marks_for_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        selected_student = callback.data.split("_")[3]
        await state.update_data(selected_student=selected_student)

        teacher_data = await get_teacher_data(callback.from_user.id)
        marks = await get_marks_for_student(selected_student, callback.from_user.id)
        if not marks:
            await callback.answer("❌ No marks found for this student.")
            return
        subject = await get_subject_by_id(teacher_data["position"])
        keyboard = marks_keyboard(
            [
                {
                    "id": mark["id"],
                    "subject": subject["name"],
                    "mark": mark["mark"],
                }
                for mark in marks
            ],
            "delete_mark",
        )
        await callback.message.edit_text(
            text="Select a mark to delete:", reply_markup=keyboard
        )
        await state.set_state(Mark.select_mark)
    except Exception as e:
        await callback.answer(f"❌ Error loading marks: {e}")


@delete_mark_router.callback_query(lambda c: c.data.startswith("delete_mark_mark_"))
async def confirm_mark_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        mark_id = callback.data.split("_")[3]
        await state.update_data(mark_id=mark_id)

        keyboard = confirm_keyboard("delete_mark")
        await callback.message.edit_text(
            text="Are you sure you want to delete this mark?", reply_markup=keyboard
        )
        await state.set_state(Mark.confirm_deletion)
    except Exception as e:
        await callback.answer(f"❌ Error during deletion confirmation: {e}")


@delete_mark_router.callback_query(lambda c: c.data == "delete_mark_yes")
async def handle_mark_deletion(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        mark_id = data.get("mark_id")

        await delete_mark(mark_id)
        await callback.answer("✅ The mark has been successfully deleted.")
    except Exception as e:
        await callback.answer(f"❌ Failed to delete the mark: {e}")
    finally:
        await state.clear()


@delete_mark_router.callback_query(
    lambda c: c.data == "back_to_classes_select_student_marks"
)
async def back_to_classes_set_mark(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        selected_class = data.get("selected_class")

        students = await get_users_in_class(selected_class)
        if not students:
            await callback.answer("❌ No students found in this class.")
            return

        keyboard = await users_keyboard(students, "select_student_marks")
        await callback.message.edit_text(
            text="Select a student:", reply_markup=keyboard
        )
        await state.set_state(Mark.select_student)
    except Exception as e:
        await callback.answer(f"❌ Error loading students: {e}")


@delete_mark_router.callback_query(lambda c: c.data == "cancel_delete_mark")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Operation cancelled.")
    await state.clear()
