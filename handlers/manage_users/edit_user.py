from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import UpdateUser
from utils.detect_admin import is_admin
from firebase.functions.users import get_user_data, update_user_data
from keyboards.inline.users import (
    get_edit_options_keyboard,
    get_all_users,
    get_user_keyboard,
)

edit_user_router = Router()


@edit_user_router.callback_query(lambda c: c.data == "edit_user")
async def edit_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        users = await get_all_users()
        if not users:
            await callback_query.message.answer("❌ No users found.")
            return

        user_keyboard = await get_user_keyboard()
        await callback_query.message.answer(
            "<b>Select a user to edit</b>", reply_markup=user_keyboard
        )
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data.startswith("user_"))
async def process_edit_user_id(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        user_id = int(callback_query.data.split("_")[1])
        user_data = await get_user_data(user_id)
        if not user_data:
            await callback_query.message.answer("❌ No user found with this ID.")
            return

        data = await state.get_data()
        edit_user_msg_id = data.get("edit_user_msg_id")
        if edit_user_msg_id:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id, message_id=edit_user_msg_id
            )

        await callback_query.message.delete()

        await state.update_data(user_id=user_id)
        await state.update_data(user_data=user_data)

        edit_options_keyboard = get_edit_options_keyboard()

        edit_options_msg = await callback_query.message.answer(
            "<b>What would you like to edit?</b>", reply_markup=edit_options_keyboard
        )
        await state.update_data(edit_options_msg_id=edit_options_msg.message_id)
        await state.set_state(UpdateUser.edit_option)


@edit_user_router.callback_query(lambda c: c.data == "edit_fullname")
async def handle_edit_fullname(callback_query: CallbackQuery, state: FSMContext):
    fullname_msg = await callback_query.message.answer(
        "<b>Please enter the new full name:</b>"
    )
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateUser.fullname)
    await callback_query.answer()


@edit_user_router.callback_query(lambda c: c.data == "edit_username")
async def handle_edit_username(callback_query: CallbackQuery, state: FSMContext):
    username_msg = await callback_query.message.answer(
        "<b>Please enter the new username:</b>"
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateUser.username)
    await callback_query.answer()


@edit_user_router.message(UpdateUser.fullname)
async def process_edit_fullname(message: Message, state: FSMContext):
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
