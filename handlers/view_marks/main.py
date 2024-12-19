from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.inline.marks import view_marks_keyboard
from firebase.functions.users import get_user_data

view_marks_router = Router()


@view_marks_router.message(Command("view_marks"))
async def view_marks(message: Message):
    user = await get_user_data(message.from_user.id)

    if user and user["role"] == "Student":
        await message.answer(
            "<b>Choose an option to view marks</b>",
            reply_markup=view_marks_keyboard,
        )
    else:
        await message.answer("⛔ You don't have permission to use this command.")
