from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.subject import Subject
from firebase.functions.subjects import (
    update_subject,
    get_all_subjects,
    get_subject_by_id,
)
from keyboards.inline.subject import subjects_keyboard, edit_option_keyboard
from utils.main import delete_previous_message
from keyboards.inline.cancel import cancel_keyboard

route = "edit_subject"
edit_subject_router = Router()

cancel = cancel_keyboard(route)


@edit_subject_router.callback_query(lambda c: c.data == route)
async def edit_subject_start(callback_query: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.message.answer("❌ Предметы не найдены.")
        await callback_query.answer()
        return

    subject_keyboard = await subjects_keyboard(subjects, "edit_subject")
    msg = await callback_query.message.answer(
        "<b>Выберите предмет, который хотите отредактировать:</b>", reply_markup=subject_keyboard
    )
    await state.update_data(initial_msg_id=msg.message_id)
    await callback_query.answer()


@edit_subject_router.callback_query(lambda c: c.data.startswith("edit_subject_"))
async def process_edit_subject_choice(callback: CallbackQuery, state: FSMContext):
    subject_id = callback.data.split("_")[2]
    subject_data = await get_subject_by_id(subject_id)
    subject_data["id"] = subject_id

    if not subject_data:
        await callback.answer("❌ Предмет не найден.")
        await state.clear()
        return

    await state.update_data(
        subject_data=subject_data,
        last_bot_msg_id=callback.message.message_id,
    )
    await callback.message.delete()
    keyboard = await edit_option_keyboard()
    msg = await callback.message.answer(
        "<b>Что вы хотите отредактировать?</b>", reply_markup=keyboard
    )
    await state.update_data(last_bot_msg_id=msg.message_id)
    await state.set_state(Subject.edit_option)
    await callback.answer()


@edit_subject_router.callback_query(lambda c: c.data == "edit_name_of_subject")
async def handle_edit_subject_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(callback.message.chat.id, data.get("last_bot_msg_id"))

    msg = await callback.message.answer(
        "<b>Введите новое название предмета:</b>", reply_markup=cancel
    )
    await state.update_data(last_bot_msg_id=msg.message_id)
    await state.set_state(Subject.edit_new_name)


@edit_subject_router.message(Subject.edit_new_name)
async def update_subject_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(message.chat.id, data.get("last_bot_msg_id"))
    await message.delete()

    new_name = message.text.strip()
    subject_data = data["subject_data"]
    subject_data["name"] = new_name
    success = await update_subject(subject_data["id"], subject_data)
    if success:
        await message.answer("<b>✅ Название предмета успешно обновлено!</b>")
    else:
        await message.answer("<b>❌ Не удалось обновить название предмета.</b>")

    await state.clear()


@edit_subject_router.callback_query(lambda c: c.data == "cancel_edit_subject")
async def cancel_edit_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer("❌ Редактирование предмета отменено.")

    await delete_previous_message(callback.message.chat.id, data.get("last_bot_msg_id"))
    await delete_previous_message(callback.message.chat.id, data.get("initial_msg_id"))

    await state.clear()
