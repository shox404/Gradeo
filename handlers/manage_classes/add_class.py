from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import ClassState
from utils.detect_admin import is_admin
from firebase.functions.classes import save_class_data

add_class_router = Router()


@add_class_router.callback_query(lambda c: c.data == "add_class")
async def add_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        name_msg = await callback_query.message.answer(
            "<b>Please enter the class name (unique).</b>"
        )
        await state.update_data(name_msg_id=name_msg.message_id)
        await state.set_state(ClassState.name)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@add_class_router.message(ClassState.name)
async def process_name(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        name_msg_id = data.get("name_msg_id")
        if name_msg_id:
            await message.bot.delete_message(message.chat.id, name_msg_id)

        await state.update_data(name=message.text)

        await message.delete()

        teacher_msg = await message.answer(
            "<b>Please enter the class teacher's name.</b>"
        )
        await state.update_data(teacher_msg_id=teacher_msg.message_id)
        await state.set_state(ClassState.teacher)


@add_class_router.message(ClassState.teacher)
async def process_teacher(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()

        teacher_msg_id = data.get("teacher_msg_id")
        if teacher_msg_id:
            await message.bot.delete_message(message.chat.id, teacher_msg_id)

        await message.delete()

        await state.update_data(teacher=message.text)

        updated_data = await state.get_data()

        await message.answer("<b>Class has been successfully added!</b>")

        name = updated_data.get("name")
        teacher = updated_data.get("teacher")

        await save_class_data({"name": name, "teacher": teacher})

        await state.clear()