from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import ClassState
from utils.detect_admin import is_admin
from firebase.functions.classes import (
    update_class_data,
    get_class_data,
    get_all_classes,
)
from keyboards.inline.classes import classes_keyboard, edit_option_keyboard

edit_class_router = Router()


@edit_class_router.callback_query(lambda c: c.data == "update_class")
async def edit_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        classes = await get_all_classes()
        if not classes:
            await callback_query.message.answer("❌ No classes found.")
            return

        class_keyboard = await classes_keyboard(classes, "edit")
        msg = await callback_query.message.answer(
            "<b>Please select the class you want to edit</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(initial_msg_id=msg.message_id)
        await callback_query.answer()
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@edit_class_router.callback_query(lambda c: str(c.data).startswith("class_edit_"))
async def process_edit_class_choice(callback_query: CallbackQuery, state: FSMContext):
    class_id = callback_query.data[11::]
    class_data = await get_class_data(class_id)

    if class_data:
        await state.update_data(
            class_data=class_data, last_bot_msg_id=callback_query.message.message_id
        )
        await callback_query.message.delete()

        msg = await callback_query.message.answer(
            "<b>What would you like to edit?</b>", reply_markup=edit_option_keyboard
        )
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.edit_option)
    else:
        await callback_query.message.answer(
            "❌ Class not found. Please check the name and try again."
        )
        await state.clear()

    await callback_query.answer()


@edit_class_router.callback_query(
    lambda c: c.data in ["edit_class_name", "edit_teacher_name", "cancel_edit_class"]
)
async def process_edit_option(callback_query: CallbackQuery, state: FSMContext):
    choice = callback_query.data
    data = await state.get_data()
    last_bot_msg_id = data.get("last_bot_msg_id")
    initial_msg_id = data.get("initial_msg_id")

    if choice == "cancel_edit_class":
        if initial_msg_id:
            await callback_query.bot.delete_message(
                callback_query.message.chat.id, initial_msg_id
            )

        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="❌ Class edition canceled.",
        )

        await state.clear()
        return

    if last_bot_msg_id:
        await callback_query.message.bot.delete_message(
            callback_query.message.chat.id, last_bot_msg_id
        )

    if choice == "edit_class_name":
        msg = await callback_query.message.answer(
            "<b>Please enter the new class name.</b>"
        )
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.new_name)
    elif choice == "edit_teacher_name":
        msg = await callback_query.message.answer(
            "<b>Please enter the new teacher's name.</b>"
        )
        await state.update_data(last_bot_msg_id=msg.message_id)
        await state.set_state(ClassState.new_teacher)

    await callback_query.answer()


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

    success = await update_class_data(
        class_data["id"], {"name": new_name, "teacher": class_data["teacher"]}
    )

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

    success = await update_class_data(
        class_data["id"], {"name": class_data["name"], "teacher": new_teacher}
    )

    if success:
        await message.answer("<b>✅ Teacher name has been successfully updated!</b>")
    else:
        await message.answer("❌ Failed to update the teacher's name.")

    await state.clear()
