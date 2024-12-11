import random
import string
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from states.class_state import Class
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions import save_class_data

add_class_router = Router()

def generate_class_id():
    """Generate a unique class ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@add_class_router.message(Command("add_class"))
async def add_class_start(message: Message, state: FSMContext):
    if await is_admin(message):
        class_name_msg = await message.answer("<b>Please enter the class name.</b>")
        await state.update_data(class_name_msg_id=class_name_msg.message_id)
        await state.set_state(Class.class_name)
    else:
        await message.answer("⛔ You don't have permission to use this command.")

@add_class_router.message(Class.class_name)
async def process_class_name(message: Message, state: FSMContext):
    if await is_admin(message):
        class_name = message.text
        await state.update_data(class_name=class_name)

        data = await state.get_data()
        class_name_msg_id = data.get("class_name_msg_id")
        if class_name_msg_id:
            await message.bot.delete_message(message.chat.id, class_name_msg_id)

        class_id = generate_class_id()
        await state.update_data(class_id=class_id)

        teacher_name_msg = await message.answer("<b>Please enter the teacher's name.</b>")
        await state.update_data(teacher_name_msg_id=teacher_name_msg.message_id)
        await state.set_state(Class.teacher_name)

@add_class_router.message(Class.teacher_name)
async def process_teacher_name(message: Message, state: FSMContext):
    if await is_admin(message):
        teacher_name = message.text
        await state.update_data(teacher_name=teacher_name)

        data = await state.get_data()
        teacher_name_msg_id = data.get("teacher_name_msg_id")
        if teacher_name_msg_id:
            await message.bot.delete_message(message.chat.id, teacher_name_msg_id)

        class_type_msg = await message.answer("<b>Please enter the class type (e.g., Online, In-person).</b>")
        await state.update_data(class_type_msg_id=class_type_msg.message_id)
        await state.set_state(Class.class_type)

@add_class_router.message(Class.class_type)
async def process_class_type(message: Message, state: FSMContext):
    if await is_admin(message):
        class_type = message.text
        await state.update_data(class_type=class_type)

        data = await state.get_data()
        class_type_msg_id = data.get("class_type_msg_id")
        if class_type_msg_id:
            await message.bot.delete_message(message.chat.id, class_type_msg_id)

        class_name = data.get("class_name")
        class_id = data.get("class_id")
        teacher_name = data.get("teacher_name")
        class_type = data.get("class_type")

        class_info = (
            f"<b>New class created:</b>\n"
            f"📚 <b>Class Name:</b> {class_name}\n"
            f"🆔 <b>Class ID:</b> {class_id}\n"
            f"👨‍🏫 <b>Teacher:</b> {teacher_name}\n"
            f"📑 <b>Class Type:</b> {class_type}"
        )

        await message.answer(class_info)

        await save_class_data({
            "class_name": class_name,
            "class_id": class_id,
            "teacher_name": teacher_name,
            "class_type": class_type,
        })

        await state.clear()
