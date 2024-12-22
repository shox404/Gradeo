from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from states.mark import Mark
from firebase.functions.classes import get_all_classes, get_class_data
from firebase.functions.users import get_users_in_class
from firebase.functions.marks import save_mark
from keyboards.inline.classes import classes_keyboard
from keyboards.inline.users import users_keyboard
from keyboards.inline.marks import marks_keyboard
from utils.main import delete_previous_message

route = "set_mark"
set_mark_router = Router()


@set_mark_router.callback_query(lambda c: c.data == "set_mark")
async def show_classes(callback: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    if not classes:
        await callback.answer("❌ No classes found.")
        return

    keyboard = await classes_keyboard(classes, route)

    classes_keyboard_msg = await callback.message.answer(
        text="Select a class:", reply_markup=keyboard
    )
    await state.update_data(classes_keyboard_msg=classes_keyboard_msg.message_id)
    await state.set_state(Mark.select_class)
    await callback.answer()


@set_mark_router.callback_query(lambda c: c.data.startswith("set_mark_"))
async def show_students(callback: CallbackQuery, state: FSMContext):
    selected_class = callback.data.split("_")[2]
    await state.update_data(selected_class=selected_class)
    students = await get_users_in_class(selected_class)
    if not students:
        await callback.answer("❌ No students found in the class.")
        return

    keyboard = await users_keyboard(students, route)
    class_name = await get_class_data(selected_class)
    await callback.message.edit_text(
        text=f"Select a student from '{class_name['name']}'.", reply_markup=keyboard
    )
    await state.set_state(Mark.select_student)


@set_mark_router.callback_query(lambda c: c.data.startswith("student_set_mark_"))
async def select_mark(callback: CallbackQuery, state: FSMContext):
    selected_student = callback.data.split("_")[3]
    await state.update_data(selected_student=selected_student)

    keyboard = marks_keyboard([2, 3, 4, 5])

    await callback.message.edit_text(text="Select a mark:", reply_markup=keyboard)
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
        await callback.answer(
            f"✅ Mark {selected_mark} has been successfully assigned to the student."
        )
        await callback.message.delete()
    except Exception as e:
        await callback.answer(f"❌ Failed to assign the mark: {e}")

    await state.clear()


@set_mark_router.callback_query(lambda c: c.data == "back_to_classes_set_mark")
async def back_to_classes_set_mark(callback: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    if not classes:
        await callback.answer("❌ No classes found.")
        return

    keyboard = await classes_keyboard(classes, route)

    classes_keyboard_msg = await callback.message.edit_text(
        text="Select a class:", reply_markup=keyboard
    )
    await state.update_data(classes_keyboard_msg=classes_keyboard_msg.message_id)
    await state.set_state(Mark.select_class)
    await callback.answer()


@set_mark_router.callback_query(lambda c: c.data == "back_to_student_set_mark")
async def back_to_classes_set_mark(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_class = data.get("selected_class")
    students = await get_users_in_class(selected_class)
    if not students:
        await callback.answer("❌ No students found in the class.")
        return

    keyboard = await users_keyboard(students, route)
    class_name = await get_class_data(selected_class)
    await callback.message.edit_text(
        text=f"Select a student from '{class_name['name']}'.", reply_markup=keyboard
    )
    await state.set_state(Mark.select_student)


@set_mark_router.callback_query(lambda c: c.data == "cancel_set_mark")
async def cancel_add_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = callback.message.chat.id

    await callback.answer("❌ Set mark process has been canceled.")

    await delete_previous_message(chat_id, data.get("selected_student"))
    await delete_previous_message(chat_id, data.get("classes_keyboard_msg"))
    await delete_previous_message(chat_id, data.get("selected_class"))

    await state.clear()
