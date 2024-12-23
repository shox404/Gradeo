from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.subject import Subject
from utils.detect_admin import is_admin
from firebase.functions.subjects import save_subject_data
from keyboards.inline.cancel import cancel_keyboard
from utils.main import delete_previous_message

route = "add_subject"
add_subject_router = Router()

cancel = cancel_keyboard(route)


@add_subject_router.callback_query(lambda c: c.data == route)
async def add_class_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        name_msg = await callback.message.answer(
            "<b>Введите название предмета:</b>", reply_markup=cancel
        )
        await state.update_data(name_msg_id=name_msg.message_id)
        await state.set_state(Subject.name)
    else:
        await callback.answer("⛔ У вас нет прав для выполнения этой команды.")
    await callback.answer()


@add_subject_router.message(Subject.name)
async def process_name(message: Message, state: FSMContext):
    if await is_admin(message):
        data = await state.get_data()
        await delete_previous_message(message.chat.id, data.get("name_msg_id"))

        await message.delete()

        await save_subject_data({"name": message.text})

        await message.answer("<b>✅ Предмет успешно добавлен!</b>")
        await state.clear()


@add_subject_router.callback_query(lambda c: c.data == "cancel_add_subject")
async def cancel_add_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = callback.message.chat.id

    await callback.answer("❌ Создание предмета отменено.")

    await delete_previous_message(chat_id, data.get("name_msg_id"))

    await state.clear()
