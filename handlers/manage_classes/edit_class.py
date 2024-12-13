from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import ClassState
from utils.detect_admin import is_admin
from firebase.functions.classes import update_class_data, get_class_data

edit_class_router = Router()


@edit_class_router.callback_query(lambda c: c.data == "update_class")
async def edit_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        msg = await callback_query.message.answer(
            "<b>Please enter the unique class name you want to edit.</b>"
        )
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.edit_choice)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@edit_class_router.message(ClassState.edit_choice)
async def process_edit_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")

    if last_bot_msg_id:
        await message.bot.delete_message(message.chat.id, last_bot_msg_id)
    await message.delete()

    class_name = message.text.strip()

    class_data = await get_class_data(class_name)

    if class_data:
        await state.update_data(original_name=class_name, class_data=class_data)

        msg = await message.answer(
            "<b>What would you like to edit?</b>\n"
            "1. Class Name\n"
            "2. Teacher Name\n"
        )
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.edit_option)
    else:
        await message.answer("❌ Class not found. Please check the name and try again.")
        await state.clear()


@edit_class_router.message(ClassState.edit_option)
async def process_edit_option(message: Message, state: FSMContext):
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")

    if last_bot_msg_id:
        await message.bot.delete_message(message.chat.id, last_bot_msg_id)
    await message.delete()

    choice = message.text.strip()

    if choice == "1":
        msg = await message.answer("<b>Please enter the new class name.</b>")
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.new_name)
    elif choice == "2":
        msg = await message.answer("<b>Please enter the new teacher's name.</b>")
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.new_teacher)
    else:
        msg = await message.answer("❌ Invalid option. Please reply with '1' or '2'.")
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.edit_option)


@edit_class_router.message(ClassState.new_name)
async def update_class_name(message: Message, state: FSMContext):
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")

    if last_bot_msg_id:
        await message.bot.delete_message(message.chat.id, last_bot_msg_id)
    await message.delete()

    new_name = message.text.strip()
    class_data = data["class_data"]

    class_data["name"] = new_name

    success = await update_class_data(class_data["id"], {"name": new_name, "teacher": class_data["teacher"]})

    if success:
        await message.answer("<b>✅ Class name has been successfully updated!</b>")
    else:
        await message.answer("❌ Failed to update the class name.")
    
    await state.clear()


@edit_class_router.message(ClassState.new_teacher)
async def update_teacher_name(message: Message, state: FSMContext):
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")

    if last_bot_msg_id:
        await message.bot.delete_message(message.chat.id, last_bot_msg_id)
    await message.delete()

    new_teacher = message.text.strip()
    class_data = data["class_data"]

    class_data["teacher"] = new_teacher

    success = await update_class_data(class_data["id"], {"name": class_data["name"], "teacher": new_teacher})

    if success:
        await message.answer("<b>✅ Teacher name has been successfully updated!</b>")
    else:
        await message.answer("❌ Failed to update the teacher's name.")

    await state.clear()
