from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from states.user import UpdateTeacher
from firebase.functions.users import (
    get_teacher_data,
    update_teacher_data,
    get_teachers_by_subject,
)
from firebase.functions.subjects import get_all_subjects, get_subject_by_id
from keyboards.inline.cancel import cancel_keyboard
from keyboards.inline.users import teacher_keyboard, edit_teacher_options_keyboard
from keyboards.inline.subject import subject_keyboard
from utils.main import delete_previous_message

route = "edit_teacher"
edit_teacher_router = Router()

cancel = cancel_keyboard(route)


def position_selection_keyboard(subjects, teacher_id: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=subj["name"],
                callback_data=f"change_position_{teacher_id}_{subj['id']}",
            )
        ]
        for subj in subjects
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к параметрам редактирования",
                callback_data=f"back_to_edit_{teacher_id}",
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@edit_teacher_router.callback_query(lambda c: c.data == "edit_teacher")
async def handle_edit_teacher(callback_query: CallbackQuery):
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.message.answer("❌ Нет доступных предметов.")
        return

    keyboard = subject_keyboard(subjects)
    await callback_query.message.answer(
        "<b>Выберите предмет для редактирования преподавателей:</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("select_subject_"))
async def handle_subject_selection(callback_query: CallbackQuery, state: FSMContext):
    subject_id = callback_query.data.split("_")[2]
    teachers = await get_teachers_by_subject(subject_id)
    if not teachers:
        await callback_query.answer("❌ Преподаватели для этого предмета не найдены.")
        return

    keyboard = await teacher_keyboard(teachers, f"{route}_{subject_id}")
    await callback_query.message.edit_text(
        "<b>Выберите преподавателя для редактирования.</b>", reply_markup=keyboard
    )
    await state.update_data(selected_subject=subject_id)
    await callback_query.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("teacher_edit_teacher"))
async def handle_teacher_selection(callback: CallbackQuery, state: FSMContext):
    teacher_id = callback.data.split("_")[4]
    teacher_data = await get_teacher_data(teacher_id)

    if not teacher_data:
        await callback.answer("❌ Преподаватель не найден.")
        return

    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)

    keyboard = edit_teacher_options_keyboard(teacher_id)
    position = await get_subject_by_id(teacher_data.get("position"))
    await callback.message.edit_text(
        f"Ф.И.О.: {teacher_data.get('fullname', 'N/A')}\n"
        f"Имя пользователя: {teacher_data.get('username', 'N/A')}\n"
        f"Должность: {position['name']}\n",
        reply_markup=keyboard,
    )
    await callback.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_fullname_"))
async def handle_edit_teacher_fullname(
    callback_query: CallbackQuery, state: FSMContext
):
    teacher_id = callback_query.data.split("_")[2]
    await state.update_data(teacher_id=teacher_id)
    fullname_msg = await callback_query.message.answer(
        "<b>Пожалуйста, введите новое полное имя</b>"
    )
    await state.update_data(fullname_msg_id=fullname_msg.message_id)
    await state.set_state(UpdateTeacher.fullname)
    await callback_query.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_username_"))
async def handle_edit_teacher_username(
    callback_query: CallbackQuery, state: FSMContext
):
    teacher_id = callback_query.data.split("_")[2]
    await state.update_data(teacher_id=teacher_id)
    username_msg = await callback_query.message.answer(
        "<b>Пожалуйста, введите новый имя пользователя</b>"
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(UpdateTeacher.username)
    await callback_query.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("edit_position_"))
async def handle_edit_teacher_position(
    callback_query: CallbackQuery, state: FSMContext
):
    teacher_id = callback_query.data.split("_")[2]
    subjects = await get_all_subjects()
    if not subjects:
        await callback_query.answer("❌ Нет доступных предметов.")
        return

    keyboard = position_selection_keyboard(subjects, teacher_id)
    await callback_query.message.edit_text(
        "<b>Выберите новую должность для преподавателя:</b>", reply_markup=keyboard
    )
    await callback_query.answer()


@edit_teacher_router.message(UpdateTeacher.fullname)
async def process_edit_teacher_fullname(message: Message, state: FSMContext):
    new_fullname = message.text
    data = await state.get_data()
    teacher_id = data["teacher_id"]

    await update_teacher_data(teacher_id, {"fullname": new_fullname})

    fullname_msg_id = data.get("fullname_msg_id")
    if fullname_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, fullname_msg_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")
    await message.delete()

    await message.answer(f"✅ Полное имя обновлено на: {new_fullname}")
    await state.clear()


@edit_teacher_router.message(UpdateTeacher.username)
async def process_edit_teacher_username(message: Message, state: FSMContext):
    new_username = message.text
    data = await state.get_data()
    teacher_id = data["teacher_id"]

    await update_teacher_data(teacher_id, {"username": new_username})

    username_msg_id = data.get("username_msg_id")
    if username_msg_id:
        try:
            await message.bot.delete_message(message.from_user.id, username_msg_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")
    await message.delete()

    await message.answer(f"✅ Имя пользователя обновлено на: @{new_username}")
    await state.clear()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("change_position_"))
async def process_change_teacher_position(callback_query: CallbackQuery):
    _, _, teacher_id, new_subject_id = callback_query.data.split("_")
    await update_teacher_data(teacher_id, {"position": new_subject_id})

    await callback_query.answer("✅ Должность преподавателя обновлена.")


@edit_teacher_router.callback_query(lambda c: c.data == "back_edit_to_teachers")
async def back_edit_to_teachers(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subject_id = data.get("selected_subject")
    teachers = await get_teachers_by_subject(subject_id)

    if not teachers:
        await callback.answer("❌ Преподаватели не найдены.")
        return

    keyboard = await teacher_keyboard(teachers, f"{route}_{subject_id}")
    await callback.message.edit_text(
        "<b>Выберите преподавателя для редактирования:</b>", reply_markup=keyboard
    )
    await callback.answer()


@edit_teacher_router.callback_query(
    lambda c: c.data.startswith("back_to_subjects_edit_teacher")
)
async def back_to_subjects_edit_teacher(callback: CallbackQuery, state: FSMContext):
    subjects = await get_all_subjects()
    if not subjects:
        await callback.message.answer("❌ Нет доступных предметов.")
        return

    keyboard = subject_keyboard(subjects)
    await callback.message.edit_text(
        "<b>Выберите предмет для редактирования преподавателей:</b>", reply_markup=keyboard
    )
    await callback.answer()


@edit_teacher_router.callback_query(lambda c: c.data.startswith("back_to_edit_"))
async def back_to_teacher_edit_options(callback: CallbackQuery, state: FSMContext):
    teacher_id = callback.data.split("_")[3]
    teacher_data = await get_teacher_data(teacher_id)

    if not teacher_data:
        await callback.answer("❌ Преподаватель не найден.")
        return

    await state.update_data(teacher_id=teacher_id, teacher_data=teacher_data)

    keyboard = edit_teacher_options_keyboard(teacher_id)
    position = await get_subject_by_id(teacher_data.get("position"))

    await callback.message.edit_text(
        f"Ф.И.О.: {teacher_data.get('fullname', 'N/A')}\n"
        f"Имя пользователя: {teacher_data.get('username', 'N/A')}\n"
        f"Должность: {position['name']}\n",
        reply_markup=keyboard,
    )
    await callback.answer()


@edit_teacher_router.callback_query(lambda c: c.data == "cancel_select_subject")
async def cancel_edit_student(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids_to_delete = [
        data.get("fullname_msg_id"),
        data.get("user_id_msg_id"),
        data.get("username_msg_id"),
        data.get("classes_msg_id"),
    ]

    await callback.answer("❌ Процесс редактирования преподавателя отменен.")

    for msg_id in msg_ids_to_delete:
        await delete_previous_message(callback.message.chat.id, msg_id)

    await state.clear()
