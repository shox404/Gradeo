from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states.user import UpdateUser
from utils.detect_admin import is_admin
from firebase.functions.users import get_user_data, update_user_data, get_users_in_class
from firebase.functions.classes import get_all_classes
from keyboards.inline.users import class_keyboard, user_keyboard, edit_options_keyboard

edit_user_router = Router()

@edit_user_router.callback_query(lambda c: c.data == "edit_user")
async def edit_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        classes = await get_all_classes()
        if not classes:
            await callback_query.message.answer("❌ No classes found.")
            return
        keyboard = await class_keyboard(classes)
        await state.update_data(current_step="menu")
        await callback_query.message.answer("<b>Select a class to edit students</b>", reply_markup=keyboard)
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data.startswith("class_"))
async def process_class_selection(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        class_id = callback_query.data.split("_")[1]
        students = await get_users_in_class(class_id)
        if not students:
            await callback_query.message.answer("❌ No students found in this class.")
            return
        student_keyboard = await user_keyboard(students)
        await state.update_data(current_step="classes", selected_class=class_id)
        await callback_query.message.edit_text("<b>Select a student to edit</b>", reply_markup=student_keyboard)
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data.startswith("student_"))
async def process_student_selection(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        student_id = callback_query.data.split("_")[1]
        student_data = await get_user_data(student_id)
        if not student_data:
            await callback_query.message.edit_text("❌ No student found with this ID.")
            return
        await state.update_data(current_step="students", student_id=student_id, student_data=student_data)
        await callback_query.message.edit_text(
            "<b>What would you like to edit for this student?</b>", reply_markup=edit_options_keyboard
        )
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data == "edit_fullname")
async def handle_edit_fullname(callback_query: CallbackQuery, state: FSMContext):
    fullname_msg = await callback_query.message.answer("<b>Please enter the new full name:</b>")
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateUser.fullname)
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data == "edit_username")
async def handle_edit_username(callback_query: CallbackQuery, state: FSMContext):
    username_msg = await callback_query.message.answer("<b>Please enter the new username:</b>")
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateUser.username)
    await callback_query.answer()

@edit_user_router.message(UpdateUser.fullname)
async def process_edit_fullname(message: Message, state: FSMContext):
    new_fullname = message.text
    data = await state.get_data()
    student_id = data["student_id"]
    await update_user_data(student_id, {"fullname": new_fullname})
    await message.answer(f"✅ Full name updated to: {new_fullname}")
    await state.clear()

@edit_user_router.message(UpdateUser.username)
async def process_edit_username(message: Message, state: FSMContext):
    new_username = message.text
    data = await state.get_data()
    student_id = data["student_id"]
    await update_user_data(student_id, {"username": new_username})
    await message.answer(f"✅ Username updated to: @{new_username}")
    await state.clear()

@edit_user_router.callback_query(lambda c: c.data == "back_to_classes")
async def back_to_classes(callback_query: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    keyboard = await class_keyboard(classes)
    await callback_query.message.edit_text("<b>Select a class to edit students</b>", reply_markup=keyboard)
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data == "back_to_students")
async def back_to_students(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_id = data.get("selected_class")
    students = await get_users_in_class(class_id)
    student_keyboard = await user_keyboard(students)
    await callback_query.message.edit_text("<b>Select a student to edit</b>", reply_markup=student_keyboard)
    await callback_query.answer()

@edit_user_router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: CallbackQuery, state: FSMContext):
    classes = await get_all_classes()
    keyboard = await class_keyboard(classes)
    await callback_query.message.edit_text("<b>Select a class to edit students</b>", reply_markup=keyboard)
    await state.update_data(current_step="menu")
    await callback_query.answer()
