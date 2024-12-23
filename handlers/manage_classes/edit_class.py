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
from utils.main import delete_previous_message
from keyboards.inline.cancel import cancel_keyboard

route = "edit_class"
edit_class_router = Router()

cancel = cancel_keyboard(route)


@edit_class_router.callback_query(lambda c: c.data == route)
async def edit_class_start(callback_query: CallbackQuery, state: FSMContext):
    if not await is_admin(callback_query):
        await callback_query.message.answer(
            "⛔ У вас нет прав для использования этой команды."
        )
        await callback_query.answer()
        return

    classes = await get_all_classes()
    if not classes:
        await callback_query.message.answer("❌ Классы не найдены.")
        await callback_query.answer()
        return

    class_keyboard = await classes_keyboard(classes, "edit_class")
    msg = await callback_query.message.answer(
        "<b>Выберите класс, который хотите редактировать</b>",
        reply_markup=class_keyboard,
    )
    await state.update_data(initial_msg_id=msg.message_id)
    await callback_query.answer()


@edit_class_router.callback_query(lambda c: c.data.startswith(route))
async def process_edit_class_choice(callback: CallbackQuery, state: FSMContext):
    class_id = callback.data.split("_")[2]
    class_data = await get_class_data(class_id)

    if not class_data:
        await callback.answer("❌ Класс не найден.")
        await state.clear()
        return

    await state.update_data(
        class_data=class_data, last_bot_msg_id=callback.message.message_id
    )
    await callback.message.delete()

    msg = await callback.message.answer(
        "<b>Что вы хотите редактировать?</b>", reply_markup=edit_option_keyboard
    )
    await state.update_data(last_bot_msg_id=msg.message_id)
    await state.set_state(ClassState.edit_option)
    await callback.answer()


@edit_class_router.callback_query(lambda c: c.data == "manage_classes_edit_class_name")
async def handle_edit_class_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(callback.message.chat.id, data.get("last_bot_msg_id"))

    msg = await callback.message.answer("<b>Введите новое имя класса.</b>")
    await state.update_data(last_bot_msg_id=msg.message_id)
    await state.set_state(ClassState.edit_new_name)


@edit_class_router.callback_query(
    lambda c: c.data == "manage_classes_edit_teacher_name"
)
async def handle_edit_teacher_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(callback.message.chat.id, data.get("last_bot_msg_id"))

    msg = await callback.message.answer("<b>Введите новое имя учителя.</b>")
    await state.update_data(last_bot_msg_id=msg.message_id)
    await state.set_state(ClassState.edit_new_teacher)


@edit_class_router.message(ClassState.edit_new_name)
async def update_class_name(message: Message, state: FSMContext):
    await process_update(message, state, "name", "Имя класса успешно обновлено!")


@edit_class_router.message(ClassState.edit_new_teacher)
async def update_teacher_name(message: Message, state: FSMContext):
    await process_update(message, state, "teacher", "Имя учителя успешно обновлено!")


async def process_update(
    message: Message, state: FSMContext, field: str, success_msg: str
):
    """Helper function to update class data."""
    data = await state.get_data()
    await delete_previous_message(message.chat.id, data.get("last_bot_msg_id"))
    await message.delete()

    new_value = message.text.strip()
    class_data = data["class_data"]
    class_data[field] = new_value

    update_data = {"name": class_data["name"], "teacher": class_data["teacher"]}
    success = await update_class_data(class_data["id"], update_data)

    if success:
        await message.answer(f"<b>✅ {success_msg}</b>")
    else:
        await message.answer(f"❌ Не удалось обновить {field}.")

    await state.clear()


@edit_class_router.callback_query(lambda c: c.data == "cancel_edit_class")
async def handle_cancel_edit_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.answer("❌ Редактирование класса отменено.")

    await delete_previous_message(callback.message.chat.id, data.get("last_bot_msg_id"))
    await delete_previous_message(callback.message.chat.id, data.get("initial_msg_id"))

    await state.clear()
