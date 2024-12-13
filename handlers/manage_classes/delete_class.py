from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import DeleteClass
from utils.detect_admin import is_admin
from firebase.functions.classes import (
    delete_class_data,
    get_class_data,
    get_all_classes,
)
from keyboards.inline.classes import classes_keyboard, delete_confirmation_keyboard

delete_class_router = Router()


@delete_class_router.callback_query(lambda c: c.data == "delete_class")
async def delete_class_start(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        classes = await get_all_classes()
        if not classes:
            await callback_query.message.answer("❌ No classes found.")
            return

        class_keyboard = await classes_keyboard(classes, "delete_unique")
        delete_class_msg = await callback_query.message.answer(
            "<b>Please select the class you want to delete</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(delete_class_msg_id=delete_class_msg.message_id)
    else:
        await callback_query.message.answer(
            "⛔ You don't have permission to use this command."
        )
    await callback_query.answer()


@delete_class_router.callback_query(lambda c: str(c.data).startswith("class_delete_unique_"))
async def process_delete_class_choice(callback_query: CallbackQuery, state: FSMContext):
    class_id = callback_query.data.split("_")[4]
    class_data = await get_class_data(class_id)

    if class_data:
        await state.update_data(class_data=class_data)

        delete_class_msg_id = (await state.get_data()).get("delete_class_msg_id")
        if delete_class_msg_id:
            await callback_query.bot.delete_message(
                callback_query.message.chat.id, delete_class_msg_id
            )

        confirm_delete_msg = await callback_query.message.answer(
            f"Are you sure you want to delete the class named '{class_data['name']}'?\n",
            reply_markup=delete_confirmation_keyboard,
        )
        await state.update_data(
            confirm_unique_msg_id=confirm_delete_msg.message_id,
            last_msg_id=confirm_delete_msg.message_id,
        )
        await state.set_state(DeleteClass.confirm_delete)
    else:
        await callback_query.message.answer("❌ Class not found. Please try again.")
        await state.clear()
    await callback_query.answer()


@delete_class_router.callback_query(
    lambda c: c.data
    in ["confirm_class_delete_yes", "confirm_class_delete_no", "cancel_delete_class"]
)
async def confirm_delete_class(callback_query: CallbackQuery, state: FSMContext):
    if await is_admin(callback_query):
        data = await state.get_data()
        class_name = data.get("name")
        class_data = data.get("class_data")
        confirm_class_delete_msg_id = data.get("confirm_class_delete_msg_id")
        delete_class_msg_id = data.get("delete_class_msg_id")

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
                    text=f"✅ Class has been deleted.",
                )
            else:
                await callback_query.bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="❌ Failed to delete class. The class may not exist.",
                )
        else:
            if delete_class_msg_id:
                await callback_query.bot.delete_message(
                    chat_id=callback_query.message.chat.id,
                    message_id=delete_class_msg_id,
                )
            await callback_query.bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Class deletion canceled.",
            )

        await state.clear()

    await callback_query.answer()
