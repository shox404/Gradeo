from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import UpdateUser
from utils.detect_admin import is_admin
from firebase.functions import get_user_data, update_user_data
from keyboards.default.role import role_keyboard

edit_user_router = Router()


@edit_user_router.callback_query(lambda c: c.data == "edit_user")
async def edit_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        edit_user_msg = await callback_query.message.answer(
            "<b>Please enter the user ID of the user you want to edit.</b>"
        )
        await state.update_data(edit_user_msg_id=edit_user_msg.message_id)
        await state.set_state(UpdateUser.user_id)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@edit_user_router.message(UpdateUser.user_id)
async def process_edit_user_id(message: Message, state: FSMContext):
    if await is_admin(message):
        try:
            user_id = int(message.text)
            user_data = await get_user_data(user_id)
            if not user_data:
                await message.answer("❌ No user found with this ID.")
                return

            data = await state.get_data()
            edit_user_msg_id = data.get("edit_user_msg_id")
            if edit_user_msg_id:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=edit_user_msg_id
                )

            await message.delete()

            await state.update_data(user_id=user_id)
            await state.update_data(user_data=user_data)

            edit_options_msg = await message.answer(
                "<b>What would you like to edit?</b>\n"
                "1. Full Name\n"
                "2. Username\n"
                "3. Role\n",
                reply_markup=None,
            )
            await state.update_data(edit_options_msg_id=edit_options_msg.message_id)
            await state.set_state(UpdateUser.edit_option)

        except ValueError:
            await message.answer(
                "❌ Invalid user ID. Please enter a valid numeric user ID."
            )


@edit_user_router.message(UpdateUser.edit_option)
async def process_edit_option(message: Message, state: FSMContext):
    if await is_admin(message):
        option = message.text.strip()

        data = await state.get_data()
        edit_options_msg_id = data.get("edit_options_msg_id")
        if edit_options_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=edit_options_msg_id
            )

        await message.delete()

        if option == "1":
            fullname_msg = await message.answer(
                "<b>Please enter the new full name:</b>"
            )
            await state.update_data(fullname_msg_id=fullname_msg.message_id)
            await state.set_state(UpdateUser.fullname)
        elif option == "2":
            username_msg = await message.answer("<b>Please enter the new username:</b>")
            await state.update_data(username_msg_id=username_msg.message_id)
            await state.set_state(UpdateUser.username)
        elif option == "3":
            role_msg = await message.answer(
                "<b>Please select the new role:</b>", reply_markup=role_keyboard
            )
            await state.update_data(role_msg_id=role_msg.message_id)
            await state.set_state(UpdateUser.role)
        else:
            await message.answer("❌ Invalid option. Please choose 1, 2, or 3.")


@edit_user_router.message(UpdateUser.fullname)
async def process_edit_fullname(message: Message, state: FSMContext):
    if await is_admin(message):
        new_fullname = message.text

        data = await state.get_data()
        fullname_msg_id = data.get("fullname_msg_id")
        if fullname_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=fullname_msg_id
            )

        await message.delete()

        await state.update_data(fullname=new_fullname)

        user_id = data.get("user_id")
        updated_data = {"fullname": new_fullname}

        await update_user_data(user_id, updated_data)

        await message.answer(f"✅ Full name updated to: {new_fullname}")

        await state.clear()


@edit_user_router.message(UpdateUser.username)
async def process_edit_username(message: Message, state: FSMContext):
    if await is_admin(message):
        new_username = message.text

        data = await state.get_data()
        username_msg_id = data.get("username_msg_id")
        if username_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=username_msg_id
            )

        await message.delete()

        await state.update_data(username=new_username)

        user_id = data.get("user_id")
        updated_data = {"username": new_username}

        await update_user_data(user_id, updated_data)

        await message.answer(f"✅ Username updated to: @{new_username}")

        await state.clear()


@edit_user_router.message(UpdateUser.role)
async def process_edit_role(message: Message, state: FSMContext):
    if await is_admin(message):
        if message.text not in ["Teacher", "Student"]:
            await message.answer(
                "❌ Invalid role! Please select either 'Teacher' or 'Student'.",
                reply_markup=role_keyboard,
            )
            return

        new_role = message.text

        data = await state.get_data()
        role_msg_id = data.get("role_msg_id")
        if role_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=role_msg_id
            )

        await message.delete()

        await state.update_data(role=new_role)

        user_id = data.get("user_id")
        updated_data = {"role": new_role}

        await update_user_data(user_id, updated_data)

        await message.answer(f"✅ Role updated to: {new_role}")

        await state.clear()
