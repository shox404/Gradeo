from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import DeleteUser
from utils.detect_admin import is_admin
from firebase.functions import delete_user_data, get_user_data
from keyboards.inline.delete_confirmation_keyboard import delete_confirmation_keyboard

delete_user_router = Router()


@delete_user_router.callback_query(lambda c: c.data == "delete_user")
async def delete_user_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        delete_user_msg = await callback_query.message.answer(
            "<b>Please enter the user ID of the user you want to delete.</b>"
        )
        await state.update_data(delete_user_msg_id=delete_user_msg.message_id)
        await state.set_state(DeleteUser.user_id)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@delete_user_router.message(DeleteUser.user_id)
async def process_delete_user_id(message: Message, state: FSMContext):
    if await is_admin(message):
        try:
            user_id = int(message.text)
            user_data = await get_user_data(user_id)
            if not user_data:
                await message.answer("❌ No user found with this ID.")
                return

            data = await state.get_data()
            delete_user_msg_id = data.get("delete_user_msg_id")
            if delete_user_msg_id:
                await message.bot.delete_message(
                    chat_id=message.chat.id, message_id=delete_user_msg_id
                )

            await message.delete()

            await state.update_data(user_id=user_id)
            await state.update_data(user_data=user_data)

            confirm_delete_msg = await message.answer(
                f"Are you sure you want to delete the user with ID {user_id}?\n"
                f"Name: {user_data['fullname']}\n"
                f"Username: @{user_data['username']}",
                reply_markup=delete_confirmation_keyboard,
            )
            await state.update_data(confirm_delete_msg_id=confirm_delete_msg.message_id)
            await state.set_state(DeleteUser.confirm_delete)

        except ValueError:
            await message.answer(
                "❌ Invalid user ID. Please enter a valid numeric user ID."
            )


@delete_user_router.callback_query(
    lambda c: c.data in ["confirm_delete_yes", "confirm_delete_no"]
)
async def confirm_delete_user(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        data = await state.get_data()
        user_id = data.get("user_id")
        confirm_delete_msg_id = data.get("confirm_delete_msg_id")

        if confirm_delete_msg_id:
            await callback_query.bot.delete_message(
                chat_id=callback_query.message.chat.id, message_id=confirm_delete_msg_id
            )

        if callback_query.data == "confirm_delete_yes":
            success = await delete_user_data(user_id)
            if success:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=f"✅ User with ID {user_id} has been deleted.",
                )
            else:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="❌ Failed to delete user. User may not exist.",
                )
        else:
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ User deletion canceled.",
            )

        await state.clear()

    await callback_query.answer()
