from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import DeleteClass
from utils.detect_admin import is_admin
from firebase.functions.classes import delete_class_data, get_class_data
from keyboards.inline.delete_class_keyboard import delete_confirmation_keyboard

delete_class_router = Router()


@delete_class_router.callback_query(lambda c: c.data == "delete_class")
async def delete_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        delete_class_msg = await callback_query.message.answer(
            "<b>Please enter the name of the class you want to delete.</b>"
        )
        await state.update_data(delete_class_msg_id=delete_class_msg.message_id)
        await state.set_state(DeleteClass.name)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@delete_class_router.message(DeleteClass.name)
async def process_delete_class_name(message: Message, state: FSMContext):
    if await is_admin(message):
        class_name = message.text.strip()
        print(f"Attempting to delete class: {class_name}")

        class_data = await get_class_data(class_name)

        if not class_data:
            await message.answer(f"❌ No class found with the name '{class_name}'.")
            return

        data = await state.get_data()
        delete_class_msg_id = data.get("delete_class_msg_id")

        if delete_class_msg_id:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=delete_class_msg_id
            )

        await message.delete()

        await state.update_data(name=class_name)
        await state.update_data(class_data=class_data)

        confirm_delete_msg = await message.answer(
            f"Are you sure you want to delete the class named '{class_name}'?\n",
            reply_markup=delete_confirmation_keyboard,
        )
        await state.update_data(
            confirm_class_delete_msg_id=confirm_delete_msg.message_id
        )
        await state.set_state(DeleteClass.confirm_delete)


@delete_class_router.callback_query(
    lambda c: c.data in ["confirm_class_delete_yes", "confirm_class_delete_no"]
)
async def confirm_delete_class(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        data = await state.get_data()
        class_name = data.get("name")
        class_data = await get_class_data(class_name)
        confirm_class_delete_msg_id = data.get("confirm_class_delete_msg_id")

        if confirm_class_delete_msg_id:
            await callback_query.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=confirm_class_delete_msg_id,
            )

        if callback_query.data == "confirm_class_delete_yes":
            success = await delete_class_data(class_data["id"])
            if success:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=f"✅ Class named '{class_name}' has been deleted.",
                )
            else:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="❌ Failed to delete class. The class may not exist.",
                )
        else:
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Class deletion canceled.",
            )

        await state.clear()

    await callback_query.answer()
