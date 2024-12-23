from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.class_state import ClassState
from utils.detect_admin import is_admin
from firebase.functions.classes import save_class_data
from keyboards.inline.cancel import cancel_keyboard
from utils.main import delete_previous_message

route = "add_class"
add_class_router = Router()

cancel = cancel_keyboard(route)


@add_class_router.callback_query(lambda c: c.data == route)
async def add_class_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        name_msg = await callback.message.answer(
            "<b>Пожалуйста, введите название класса.</b>", reply_markup=cancel
        )
        await state.update_data(name_msg_id=name_msg.message_id)
        await state.set_state(ClassState.name)
    else:
        await callback.answer("⛔ У вас нет прав для использования этой команды.")
    await callback.answer()


@add_class_router.message(ClassState.name)
async def process_name(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        await delete_previous_message(message.chat.id, data.get("name_msg_id"))

        await state.update_data(name=message.text)
        await message.delete()

        teacher_msg = await message.answer(
            "<b>Пожалуйста, введите имя учителя класса.</b>", reply_markup=cancel
        )
        await state.update_data(teacher_msg_id=teacher_msg.message_id)
        await state.set_state(ClassState.teacher)


@add_class_router.message(ClassState.teacher)
async def process_teacher(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        await delete_previous_message(message.chat.id, data.get("teacher_msg_id"))
        await message.delete()

        await state.update_data(teacher=message.text)
        updated_data = await state.get_data()

        await save_class_data(
            {"name": updated_data.get("name"), "teacher": updated_data.get("teacher")}
        )

        await message.answer("<b>✅ Класс был успешно добавлен!</b>")
        await state.clear()


@add_class_router.callback_query(lambda c: c.data == "cancel_add_class")
async def cancel_add_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = callback.message.chat.id

    await callback.answer("❌ Процесс создания класса был отменен.")

    await delete_previous_message(chat_id, data.get("name_msg_id"))
    await delete_previous_message(chat_id, data.get("teacher_msg_id"))

    await state.clear()
