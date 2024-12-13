from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import UpdateUser
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions.classes import update_class_data, get_class_data

edit_class_router = Router()


@edit_class_router.callback_query(lambda c: c.data == "edit_class")
async def edit_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        edit_class_msg = await callback_query.message.answer(
            "<b>Please enter the class ID of the class you want to edit.</b>"
        )
        await state.update_data(edit_class_msg_id=edit_class_msg.message_id)
        await state.set_state(UpdateUser.user_id)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@edit_class_router.message(UpdateUser.user_id)
async def process_edit_class_id(message: Message, state: FSMContext):
    if await is_admin(message):
        try:
            class_id = int(message.text)
            class_data = await get_class_data(class_id)
            if not class_data:
                await message.answer("❌ No class found with this ID.")
                return

            data = await state.get_data()
            edit_class_msg_id = data.get("edit_class_msg_id")
            if edit_class_msg_id:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=edit_class_msg_id
                )

            await message.delete()

            await state.update_data(class_id=class_id)
            await state.update_data(class_data=class_data)

            edit_option_msg = await message.answer(
                "Which option would you like to edit?\n"
                "1. Class Name\n"
                "2. Teacher Name\n"
                "3. Class Role",
                reply_markup=role_keyboard,
            )
            await state.update_data(edit_option_msg_id=edit_option_msg.message_id)
            await state.set_state(UpdateUser.edit_option)

        except ValueError:
            await message.answer(
                "❌ Invalid class ID. Please enter a valid numeric class ID."
            )


@edit_class_router.message(UpdateUser.edit_option)
async def process_edit_option(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        edit_option_msg_id = data.get("edit_option_msg_id")
        if edit_option_msg_id:
            await message.bot.delete_message(message.chat.id, edit_option_msg_id)
        await message.delete()

        option = message.text.lower()
        await state.update_data(edit_option=option)

        if option == "1":
            name_msg = await message.answer(
                "<b>Please enter the new class name.</b>"
            )
            await state.update_data(name_msg_id=name_msg.message_id)
            await state.set_state(UpdateUser.fullname)
        elif option == "2":
            teacher_name_msg = await message.answer(
                "<b>Please enter the new teacher name.</b>"
            )
            await state.update_data(teacher_name_msg_id=teacher_name_msg.message_id)
            await state.set_state(UpdateUser.fullname)
        elif option == "3":
            role_msg = await message.answer(
                "<b>Please select the new role for the class.</b>",
                reply_markup=role_keyboard,
            )
            await state.update_data(role_msg_id=role_msg.message_id)
            await state.set_state(UpdateUser.role)
        else:
            await message.answer(
                "❌ Invalid option. Please choose one of the available options."
            )


@edit_class_router.message(UpdateUser.fullname)
async def process_name(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        name_msg_id = data.get("name_msg_id")
        if name_msg_id:
            await message.bot.delete_message(message.chat.id, name_msg_id)
        await message.delete()

        new_name = message.text
        await state.update_data(new_name=new_name)

        class_id = data.get("class_id")
        updated_data = {"name": new_name}

        await update_class_data(class_id, updated_data)

        await message.answer(f"✅ Class name has been updated to {new_name}")
        await state.clear()


@edit_class_router.message(UpdateUser.role)
async def process_class_role(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        role_msg_id = data.get("role_msg_id")
        if role_msg_id:
            await message.bot.delete_message(message.chat.id, role_msg_id)
        await message.delete()

        new_role = message.text
        await state.update_data(new_role=new_role)

        class_id = data.get("class_id")
        updated_data = {"role": new_role}

        await update_class_data(class_id, updated_data)

        await message.answer(f"✅ Class role has been updated to {new_role}")
        await state.clear()
