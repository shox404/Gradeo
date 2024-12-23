from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.user import User
from utils.detect_admin import is_admin
from keyboards.default.role import role_keyboard
from firebase.functions.users import save_user_data
from firebase.functions.classes import get_all_classes, get_class_data
from firebase.functions.subjects import get_subject_by_id
from keyboards.inline.classes import classes_keyboard
from keyboards.inline.users import subjects_keyboard
from keyboards.inline.cancel import cancel_keyboard
from utils.main import delete_previous_message

route = "add_user"
add_user_router = Router()

cancel = cancel_keyboard(route)


@add_user_router.callback_query(lambda c: c.data == route)
async def add_user_start(callback: CallbackQuery, state: FSMContext):
    if await is_admin(callback):
        fullname_msg = await callback.message.answer(
            "<b>Пожалуйста, введите полное имя.</b>", reply_markup=cancel
        )
        await state.update_data(fullname_msg_id=fullname_msg.message_id)
        await state.set_state(User.fullname)
        await callback.answer()
    else:
        await callback.answer("⛔ У вас нет прав для использования этой команды.")


@add_user_router.message(User.fullname)
async def process_fullname(message: Message, state: FSMContext):
    await delete_previous_message(
        message.chat.id, (await state.get_data()).get("fullname_msg_id")
    )
    await message.delete()
    await state.update_data(fullname=message.text)

    user_id_msg = await message.answer(
        "<b>Пожалуйста, введите ID пользователя нового пользователя.</b>", reply_markup=cancel
    )
    await state.update_data(user_id_msg_id=user_id_msg.message_id)
    await state.set_state(User.user_id)


@add_user_router.message(User.user_id)
async def process_user_id(message: Message, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(message.chat.id, data.get("user_id_msg_id"))
    await message.delete()

    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
    except ValueError:
        error_msg = await message.answer(
            "❌ Неверный ID пользователя. Пожалуйста, введите действительный числовой ID пользователя."
        )
        await state.update_data(error_msg_id=error_msg.message_id)
        return

    username_msg = await message.answer(
        "<b>Пожалуйста, введите имя пользователя нового пользователя.</b>", reply_markup=cancel
    )
    await state.update_data(username_msg_id=username_msg.message_id)
    await state.set_state(User.username)


@add_user_router.message(User.username)
async def process_username(message: Message, state: FSMContext):
    await delete_previous_message(
        message.chat.id, (await state.get_data()).get("username_msg_id")
    )
    await message.delete()

    await state.update_data(username=message.text)

    role_msg = await message.answer(
        "<b>Теперь выберите роль для нового пользователя.</b>", reply_markup=role_keyboard
    )
    await state.update_data(role_msg_id=role_msg.message_id)
    await state.set_state(User.role)


@add_user_router.message(lambda m: m.text in ["Учитель", "Студент"])
async def process_role_message(message: Message, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(message.chat.id, data.get("role_msg_id"))
    await message.delete()

    role = message.text
    await state.update_data(role=role)

    if role == "Студент":
        classes = await get_all_classes()
        class_keyboard = await classes_keyboard(classes, route)
        class_msg = await message.answer(
            "<b>Пожалуйста, выберите класс студента.</b>",
            reply_markup=class_keyboard,
        )
        await state.update_data(class_msg_id=class_msg.message_id)
        await state.set_state(User.student_class)

    elif role == "Учитель":
        subject_keyboard = await subjects_keyboard()
        subject_msg = await message.answer(
            "<b>Пожалуйста, выберите предмет учителя.</b>", reply_markup=subject_keyboard
        )
        await state.update_data(subject_msg_id=subject_msg.message_id)
        await state.set_state(User.position)


@add_user_router.callback_query(lambda c: c.data.startswith("subject_add_"))
async def process_subject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(callback.message.chat.id, data.get("subject_msg_id"))

    subject = callback.data[8:]
    await state.update_data(position=subject)
    await finalize_user_data(callback, state)
    await callback.answer()


@add_user_router.callback_query(lambda c: c.data.startswith(route))
async def process_user_class(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await delete_previous_message(callback.message.chat.id, data.get("class_msg_id"))

    class_id = callback.data.split("_")[2]
    await state.update_data(user_class=class_id)
    await finalize_user_data(callback, state)


async def finalize_user_data(
    msg_or_callback: Message | CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    fullname = data.get("fullname")
    user_id = data.get("user_id")
    username_data = data.get("username")
    username = username_data if "@" in username_data else f"@{username_data}"
    role = data.get("role")

    position = data.get("position") if role == "Учитель" else None
    class_id = data.get("user_class") if role == "Студент" else None
    user_class = await get_class_data(class_id) if class_id else None
    user_position = await get_subject_by_id(position[4:]) if position else None

    info_message = f"<b>Новый {role} добавлен</b>\n"
    info_message += f"👤 <b>Имя:</b> {fullname}\n🆔 <b>ID:</b> {user_id}\n🌐 <b>Имя пользователя:</b> {username}\n"
    if role == "Учитель" and user_position:
        info_message += f"📌 <b>Должность:</b> {user_position['name']}\n"
    if role == "Студент" and user_class:
        info_message += f"🏫 <b>Класс:</b> {user_class['name']}\n"

    if isinstance(msg_or_callback, Message):
        await msg_or_callback.answer(info_message)
    elif isinstance(msg_or_callback, CallbackQuery):
        await msg_or_callback.message.answer(info_message)

    user_data = {
        "fullname": fullname,
        "user_id": user_id,
        "username": username,
        "role": role,
    }
    if role == "Учитель" and position:
        user_data["position"] = position[4:]
    if role == "Студент" and user_class:
        user_data["class"] = user_class["id"]

    await save_user_data(user_data)
    await state.clear()


@add_user_router.callback_query(lambda c: c.data == "cancel_add_user")
async def cancel_add_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids_to_delete = [
        data.get("fullname_msg_id"),
        data.get("user_id_msg_id"),
        data.get("username_msg_id"),
        data.get("role_msg_id"),
        data.get("class_msg_id"),
    ]

    await callback.answer("❌ Процесс создания пользователя отменен.")

    for msg_id in msg_ids_to_delete:
        await delete_previous_message(callback.message.chat.id, msg_id)

    await state.clear()
