from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import ClassState
from utils.detect_admin import is_admin
from firebase.functions.classes import (
    delete_class_data,
    get_class_data,
    get_all_classes,
)
from keyboards.inline.classes import classes_keyboard, delete_confirmation_keyboard
from utils.main import delete_previous_message
from keyboards.inline.cancel import cancel_keyboard

route = "delete_class"
delete_class_router = Router()

cancel = cancel_keyboard(route)


@delete_class_router.callback_query(lambda c: c.data == route)
async def delete_class_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        classes = await get_all_classes()
        if not classes:
            await callback.message.answer("❌ No classes found.")
            await callback.answer()
            return

        class_keyboard = await classes_keyboard(classes, route)
        delete_class_msg = await callback.message.answer(
            "<b>Please select the class you want to delete</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(delete_class_msg_id=delete_class_msg.message_id)
        await callback.answer()
    else:
        await callback.answer("⛔ You don't have permission to use this command.")


@delete_class_router.callback_query(lambda c: c.data.startswith(route))
async def process_delete_class_choice(callback: CallbackQuery, state: FSMContext):
    class_id = callback.data.split("_")[2]
    class_data = await get_class_data(class_id)

    if not class_data:
        await callback.message.answer("❌ Class not found. Please try again.")
        await state.clear()
        await callback.answer()
        return

    await state.update_data(class_data=class_data)

    data = await state.get_data()
    msg_id = data.get("delete_class_msg_id")
    await delete_previous_message(callback.message.chat.id, msg_id)

    confirm_delete_msg = await callback.message.answer(
        f"Are you sure you want to delete the class named '{class_data['name']}'?\n",
        reply_markup=delete_confirmation_keyboard,
    )
    await state.update_data(confirm_delete_msg_id=confirm_delete_msg.message_id)
    await state.set_state(ClassState.delete_confirm)
    await callback.answer()


@delete_class_router.callback_query(lambda c: c.data == "confirm_class_delete_yes")
async def confirm_delete_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    class_data = data.get("class_data")

    success = await delete_class_data(class_data["id"])
    if success:
        await callback.answer("✅ Class has been deleted.")
    else:
        await callback.answer("❌ Failed to delete class. The class may not exist.")

    msg = data.get("confirm_delete_msg_id")
    await delete_previous_message(callback.message.chat.id, msg)

    await state.clear()


@delete_class_router.callback_query(lambda c: c.data == "cancel_delete_class")
async def handle_cancel_delete_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = callback.message.chat.id

    await callback.answer("❌ Class deletion canceled.")

    await delete_previous_message(chat_id, data.get("delete_class_msg_id"))
    await delete_previous_message(chat_id, data.get("confirm_delete_msg_id"))

    await state.clear()
