from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from keyboards.inline.classes import classes_keyboard
from firebase.functions.classes import get_all_classes, get_class_data
from firebase.functions.users import get_user_data, get_users_in_class
from aiogram.fsm.state import State, StatesGroup

notify_class_router = Router()


class NotifyFSM(StatesGroup):
    waiting_for_message = State()


@notify_class_router.message(Command("notify_class"))
async def manage_classes(message: Message):
    user = await get_user_data(message.from_user.id)
    if user and user["role"] == "Teacher":
        classes = await get_all_classes()
        keyboard = await classes_keyboard(classes, "notify_class")
        await message.answer("<b>Choose a class</b>", reply_markup=keyboard)
    else:
        await message.answer("⛔ You don't have permission to use this command.")


@notify_class_router.callback_query(lambda c: c.data.startswith("class_notify_class_"))
async def handle_class_selection(callback_query: CallbackQuery, state: FSMContext):
    user = await get_user_data(callback_query.from_user.id)
    if user and user["role"] == "Teacher":
        class_id = callback_query.data.split("_")[-1]
        await state.update_data(class_id=class_id)
        await callback_query.message.answer(
            "✅ Class selected. Now, please send the message to notify all students in this class."
        )
        await state.set_state(NotifyFSM.waiting_for_message)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@notify_class_router.message(NotifyFSM.waiting_for_message)
async def handle_teacher_message(message: Message, state: FSMContext):
    user = await get_user_data(message.from_user.id)
    if user and user["role"] == "Teacher":
        data = await state.get_data()
        class_id = data.get("class_id")
        students = await get_users_in_class(class_id)
        if not students:
            await message.answer("❌ No students found in this class.")
            await state.clear()
            return
        for student in students:
            try:
                print(student)
                await message.bot.send_message(
                    student["id"],
                    f"📢 <b>Notification from the teacher ({user["fullname"]}):</b>\n\n{message.text}",
                )
            except Exception as e:
                print(f"Failed to send message to {student}: {e}")
        await message.answer("✅ Your message has been sent to all students.")
        await state.clear()
    else:
        await message.answer("⛔ You don't have permission to perform this action.")
