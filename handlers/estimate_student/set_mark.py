from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.mark import Mark
from firebase.functions.classes import get_all_classes
from firebase.functions.users import get_users_in_class
from firebase.functions.marks import save_mark

set_mark_router = Router()


@set_mark_router.callback_query(lambda c: c.data == "set_mark")
async def show_classes(callback: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    if not classes:
        await callback.message.edit_text("No classes found.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                text=class_data["name"],
                callback_data=f"class_set_mark_{class_data['id']}",
            )
        ]
        for class_data in classes
    ]
    keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

    await callback.message.edit_text(
        text="Select a class:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await state.set_state(Mark.select_class)


@set_mark_router.callback_query(lambda c: c.data.startswith("class_set_mark_"))
async def show_students(callback: CallbackQuery, state: FSMContext):
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
                text=student['fullname'],
                callback_data=f"student_set_mark_{student['id']}",
            )
        ]
        for i, student in enumerate(students, start=1)
    ]
    keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

    await callback.message.edit_text(
        text=f"Select a student from '{selected_class}':",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await state.set_state(Mark.select_student)


@set_mark_router.callback_query(lambda c: c.data.startswith("student_set_mark_"))
async def select_mark(callback: CallbackQuery, state: FSMContext):
    selected_student = callback.data.split("_")[3]
    await state.update_data(selected_student=selected_student)
    marks = [2, 3, 4, 5]

    keyboard = [
        [InlineKeyboardButton(text=str(mark), callback_data=f"mark_{mark}")]
        for mark in marks
    ]
    keyboard.append([InlineKeyboardButton(text="Cancel", callback_data="cancel")])

    await callback.message.edit_text(
        text="Select a mark:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
    await state.set_state(Mark.select_mark)


@set_mark_router.callback_query(lambda c: c.data.startswith("mark_"))
async def handle_mark_selection(callback: CallbackQuery, state: FSMContext):
    selected_mark = int(callback.data.split("_")[1])
    data = await state.get_data()
    selected_student = data.get("selected_student")
    selected_class = data.get("selected_class")

    try:
        await save_mark(
            class_id=selected_class,
            student_id=selected_student,
            mark=selected_mark,
            teacher_id=callback.from_user.id,
        )
        await callback.message.edit_text(
            text=f"Mark {selected_mark} has been successfully assigned to the student.",
            reply_markup=None,
        )
    except Exception as e:
        await callback.message.edit_text(
            text=f"Failed to assign the mark: {e}", reply_markup=None
        )

    await state.clear()
