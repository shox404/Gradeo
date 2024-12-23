from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states.subject import Subject
from utils.detect_admin import is_admin
from firebase.functions.subjects import (
    delete_subject_data,
    get_subject_by_id,
    get_all_subjects,
)
from keyboards.inline.subject import subjects_keyboard, delete_confirmation_keyboard
from utils.main import delete_previous_message
from keyboards.inline.cancel import cancel_keyboard

route = "delete_subject"
delete_subject_router = Router()

cancel = cancel_keyboard(route)


@delete_subject_router.callback_query(lambda c: c.data == route)
async def delete_subject_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        subjects = await get_all_subjects()
        if not subjects:
            await callback.answer("❌ Предметы не найдены.")
            return

        subject_keyboard = await subjects_keyboard(subjects, route)
        delete_subject_msg = await callback.message.answer(
            "<b>Выберите предмет, который хотите удалить:</b>",
            reply_markup=subject_keyboard,
        )
        await state.update_data(delete_subject_msg_id=delete_subject_msg.message_id)
        await callback.answer()
    else:
        await callback.answer("⛔ У вас нет прав для выполнения этой команды.")


@delete_subject_router.callback_query(lambda c: c.data.startswith(route))
async def process_delete_subject_choice(callback: CallbackQuery, state: FSMContext):
    subject_id = callback.data.split("_")[2]
    subject_data = await get_subject_by_id(subject_id)
    subject_data["id"] = subject_id
    if not subject_data:
        await callback.answer("❌ Предмет не найден. Попробуйте снова.")
        await state.clear()
        return

    await state.update_data(subject_data=subject_data)

    data = await state.get_data()
    msg_id = data.get("delete_subject_msg_id")
    await delete_previous_message(callback.message.chat.id, msg_id)
    confirm_delete_msg = await callback.message.answer(
        "Вы уверены, что хотите удалить этот предмет?",
        reply_markup=delete_confirmation_keyboard(),
    )
    await state.update_data(confirm_delete_msg_id=confirm_delete_msg.message_id)
    await state.set_state(Subject.delete_confirm)
    await callback.answer()


@delete_subject_router.callback_query(lambda c: c.data == "confirm_subject_delete_yes")
async def confirm_delete_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_data = data.get("subject_data")
    if not subject_data:
        await callback.answer("❌ Некорректные данные предмета. Попробуйте снова.")
        await state.clear()
        return

    success = await delete_subject_data(subject_data["id"])
    if success:
        await callback.answer("✅ Предмет был удален.")
    else:
        await callback.answer("❌ Не удалось удалить предмет. Возможно, он не существует.")

    msg = data.get("confirm_delete_msg_id")
    await delete_previous_message(callback.message.chat.id, msg)

    await state.clear()


@delete_subject_router.callback_query(lambda c: c.data == "cancel_delete_subject")
async def handle_cancel_delete_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chat_id = callback.message.chat.id

    await callback.answer("❌ Удаление предмета отменено.")

    await delete_previous_message(chat_id, data.get("delete_subject_msg_id"))
    await delete_previous_message(chat_id, data.get("confirm_delete_msg_id"))

    await state.clear()
