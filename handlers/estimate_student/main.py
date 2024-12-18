from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.inline.classes import estimate_student_keyboard
from firebase.functions.users import get_user_data

estimate_student_router = Router()


@estimate_student_router.message(Command("estimate_student"))
async def manage_classes(message: Message):
    user = await get_user_data(message.from_user.id)

    if user and user["role"] == "Teacher":
        await message.answer(
            "<b>Choose an option to manage classes</b>",
            reply_markup=estimate_student_keyboard,
        )
    else:
        await message.answer("⛔ You don't have permission to use this command.")
